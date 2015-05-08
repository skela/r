
import os
import json

from r import R
from r import RUtils


class RBase(object):

    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def components_for_line(line):

        succeeded = False
        w = None
        h = None
        method = "auto"
        svg = None
        png = None
        action = None

        if not line.startswith("#"):

            sline = line
            if "|" in line:
                sline = line[0:line.find("|")]
                action = line[line.find("|")+1:len(line)]

            comps = sline.split(",")
            if not len(comps) == 0:
                if len(comps) >= 2:
                    if not RBase.is_number(comps[0]):
                        method = comps[0]
                        comps = comps[1:len(comps)]
                    if RBase.is_number(comps[0]):
                        w = comps[0]
                        comps = comps[1:len(comps)]
                    if RBase.is_number(comps[0]):
                        h = comps[0]
                        comps = comps[1:len(comps)]
                    if len(comps) > 0:
                        svg = comps[0]
                        if len(comps) > 0:
                            comps = comps[1:len(comps)]
                        succeeded = True
                    if len(comps) > 0:
                        png = comps[0]
        return succeeded, method, w, h, svg, png, action

    @staticmethod
    def script_for_line(line):
        if not line.startswith("#"):
            comps = line.split(",")
            if len(comps) == 1:
                c = comps[0]
                if c.endswith('.sh') or c.endswith('.py'):
                    return os.path.join(os.curdir, c)
        return None

    # Load File
    #   path_to_resources_file = path to the file that lists resources in the following format:
    #       w,h,sfile,png
    #       w,sfile,png
    #       w,sfile
    #       method,w,h,sfile,png
    #       method,w,sfile,png
    #   path_to_resources_folder = path to the folder containing all the input graphics
    def run_file(self, path_to_resources_file, path_to_resources_folder):
        f = open(path_to_resources_file)
        s = f.read()
        f.close()
        l = s.split("\n")
        self.run_lines(l, path_to_resources_folder)

    def run_lines(self, lines, path_to_resources_folder):

        for line in lines:

            if line.startswith('exit'):
                break

            script = RBase.script_for_line(line)
            if script is not None:
                os.system(script)

            (succeeded, method, w, h, sfile, png, action) = RBase.components_for_line(line)
            if not succeeded:
                continue

            if method is not "launch_image":
                sfile = os.path.join(path_to_resources_folder, sfile)
                if len(os.path.splitext(sfile)[1]) == 0:
                    sfile += ".svg"

            ret = None
            if method == "auto":
                if sfile.endswith(".xcf"):
                    self.xcf2pngs(w, h, sfile, png)
                elif sfile.endswith(".png"):
                    self.png2pngs(w, h, sfile, png)
                else:
                    ret = self.svg2pngs(w, h, sfile, png)
            elif method == "svg" or method == "inkscape":
                ret = self.svg2pngs(w, h, sfile, png)
            elif method == "svg2png":
                ret = self.svg2png(w, h, sfile, png)
            elif method == "ic_menu_icon":
                self.ic_menu_icon(sfile, png)
            elif method == "icon" or method == "app_icon":
                self.icon(sfile)
            elif method == "launch_image":
                sfiles = sfile.split(':')
                svg_bg = sfiles[0]
                svg_centred = sfiles[1]
                svg_bg = os.path.join(path_to_resources_folder, svg_bg)
                if len(os.path.splitext(svg_bg)[1]) == 0:
                    svg_bg += ".svg"
                svg_centred = os.path.join(path_to_resources_folder, svg_centred)
                if len(os.path.splitext(svg_centred)[1]) == 0:
                    svg_centred += ".svg"
                self.launch_image(svg_bg, svg_centred, w, h)
            elif method == "pdf":
                self.svg2pdf(sfile, png)

            if ret is not None and action is not None:
                action = action.strip()
                if "->" in action:
                    clrs = action.split("->")
                    clr_from = clrs[0]
                    clr_to = clrs[1]
                    for img in ret:
                        self.r.convert_color(img, img, clr_from, clr_to)
                elif action.startswith("-"):
                    for img in ret:
                        self.r.convert(img, img, action)

    @staticmethod
    def create_run_file_header():
        c = '''#  w,h,sfile,png
#  w,h,sfile,png|white->black
#  w,sfile,png
#  w,sfile
#  method,w,h,sfile,png
#  method,w,sfile,png
'''
        return c


class RDroid(RBase):

    def __init__(self, path_droid_resources, path_inkscape=None, path_convert=None):
        self.r = R(path_inkscape, path_convert)
        self.path_droid_resources = path_droid_resources

    @staticmethod
    def out_path_from_out_name(path_droid_resources, svg_file, out_name=None):
        dr = os.path.join(path_droid_resources, "drawable-xhdpi")
        o_name = out_name
        if o_name is None:
            icon_name = os.path.basename(svg_file)
            o_name = icon_name.replace('.svg', '.png')
        out_path = os.path.join(dr, o_name)
        return out_path

    def ic_menu_icon(self, svg_file, out_name=None):
        out_path = RDroid.out_path_from_out_name(self.path_droid_resources, svg_file, out_name)
        self.r.svg2png(64, 64, out_path, svg_file)

        in_path = out_path

        # 333333
        out_path_dark = out_path.replace(".png", "_light.png")
        self.r.convert_color(in_path, out_path_dark, 'white', "rgb(51,51,51)")

        # FFFFFF
        out_path_light = out_path.replace(".png", "_dark.png")
        self.r.convert_color(in_path, out_path_light, 'white', "rgb(255,255,255)")

        cmd = 'rm "%s"' % in_path
        os.system(cmd)

    def svg2png(self, w_1x, h_1x, svg_file, out_name=None):
        out_path = RDroid.out_path_from_out_name(self.path_droid_resources, svg_file, out_name)
        w = RUtils.number_from_object(w_1x)*2
        h = RUtils.number_from_object(h_1x)*2
        self.r.svg2png(w, h, out_path, svg_file)

    def svg2pngs(self, w_1x, h_1x, svg_file, out_name=None):
        self.svg2png(w_1x, h_1x, svg_file, out_name)

    def xcf2png(self, w_1x, h_1x, xcf_file, out_name=None):
        out_path = RDroid.out_path_from_out_name(self.path_droid_resources, xcf_file, out_name)
        w = RUtils.number_from_object(w_1x)*2
        h = RUtils.number_from_object(h_1x)*2
        self.r.xcf2png(w, h, out_path, xcf_file)

    def xcf2pngs(self, w_1x, h_1x, svg_file, out_name=None):
        self.xcf2png(w_1x, h_1x, svg_file, out_name)

    def svg2pdf(self, svg_file, out_name=None):
        print "svg2pdf is not supported on android"


class RiOS(RBase):

    def __init__(self, path_ios_resources, path_inkscape=None, path_convert=None):
        self.r = R(path_inkscape, path_convert)
        self.path_ios_resources = path_ios_resources
        self.path_ios_assets = None

    def set_ios_assets(self, path):
        self.path_ios_assets = path

    @staticmethod
    def out_path_from_out_name(path_ios_resources, source_file, out_name=None):
        dr = path_ios_resources
        o_name = out_name
        if o_name is None:
            icon_name = os.path.basename(source_file)
            icon_ext = os.path.splitext(source_file)[1]
            o_name = icon_name.replace(icon_ext, '.png')
        out_path = os.path.join(dr, o_name)
        return out_path

    @staticmethod
    def out_path_from_out_name_pdf(path_ios_resources, source_file, out_name=None):
        dr = path_ios_resources
        if 'Images.xcassets' not in dr:
            img_assets = os.path.join(dr, 'Images.xcassets')
        else:
            img_assets = dr
        if not os.path.exists(img_assets):
            exit("Failed to locate Images.xcassets at %s" % img_assets)
        if not os.path.exists(source_file):
            exit("Failed to locate %s" % source_file)
        o_name = out_name
        if o_name is None:
            icon_name = os.path.basename(source_file)
            icon_ext = os.path.splitext(source_file)[1]
            o_name = icon_name.remove(icon_ext)
        out_path = os.path.join(img_assets, o_name + '.imageset')

        if not os.path.exists(out_path):
            os.mkdir(out_path)

        d = dict()
        d["images"] = [{"idiom": "universal", "filename": o_name + ".pdf"}]
        d["info"] = {"version": 1, "author": "xcode"}
        s = json.dumps(d)
        f = open(os.path.join(out_path, "Contents.json"), 'w')
        f.write(s)
        f.close()

        out_path = os.path.join(out_path, o_name + ".pdf")

        return out_path

    def png2pngs(self, w_1x, h_1x, png_file, out_name=None):
        in_file = png_file
        out_file = RiOS.out_path_from_out_name(self.path_ios_resources, png_file, out_name)
        self.r.png2pngs_r(w_1x, h_1x, out_file, in_file)

    def svg2pngs(self, w_1x, h_1x, svg_file, out_name=None):
        in_file = svg_file
        out_file = RiOS.out_path_from_out_name(self.path_ios_resources, svg_file, out_name)
        return self.r.svg2pngs(w_1x, h_1x, out_file, in_file)

    def svg2png(self, w_1x, h_1x, svg_file, out_name=None):
        in_file = svg_file
        out_file = RiOS.out_path_from_out_name(self.path_ios_resources, svg_file, out_name)
        return self.r.svg2png(w_1x, h_1x, out_file, in_file)

    def xcf2pngs(self, w_1x, h_1x, xcf_file, out_name=None):
        in_file = xcf_file
        out_file = RiOS.out_path_from_out_name(self.path_ios_resources, xcf_file, out_name)
        self.r.xcf2pngs(w_1x, h_1x, out_file, in_file)

    def xcf2png(self, w_1x, h_1x, xcf_file, out_name=None):
        in_file = xcf_file
        out_file = RiOS.out_path_from_out_name(self.path_ios_resources, xcf_file, out_name)
        self.r.xcf2png(w_1x, h_1x, out_file, in_file)

    def svg2pdf(self, svg_file, out_name=None):
        output_folder = self.path_ios_resources
        if self.path_ios_assets is not None:
            output_folder = self.path_ios_assets
        in_file = svg_file
        out_file = RiOS.out_path_from_out_name_pdf(output_folder, svg_file, out_name)
        return self.r.svg2pdf(in_file, out_file)

    def icon(self, svg_file):
        self.r.svg2appiconset(svg_file, self.path_ios_resources)

    def launch_image(self, svg_bg, svg_centred, w, h):
        width = RUtils.number_from_object(w)
        height = RUtils.number_from_object(h)
        svg_centred_size_1x = [width, height]
        self.r.svg2launch_image(svg_bg, svg_centred, svg_centred_size_1x, self.path_ios_resources, for_iphone=True, for_ipad=True)


class RResources(RBase):

    def __init__(self, path_to_source_files=None, path_to_destination_ios=None, path_to_destination_droid=None, path_inkscape=None, path_convert=None):
        self.path_source_resources = path_to_source_files
        if path_to_destination_ios is not None:
            self.ios_resources = RiOS(path_to_destination_ios, path_inkscape, path_convert)
        if path_to_destination_droid is not None:
            self.droid_resources = RDroid(path_to_destination_droid, path_inkscape, path_convert)

    def svg2pngs(self, w_1x, h_1x, in_name, out_name=None):
        in_file = in_name
        if not os.path.exists(in_file) and self.path_to_source_files is not None:
            in_file = os.path.join(self.path_source_resources, in_name)
        if self.ios_resources is not None:
            self.ios_resources.svg2pngs(w_1x, h_1x, in_file, out_name)
        if self.droid_resources is not None:
            self.droid_resources.svg2png(w_1x, h_1x, in_file, out_name)
