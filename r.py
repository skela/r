# Utility Class to create resource recipes for image resources in iOS Projects.
#
# svg2png - Depends on Inkscape
# xcf2png - Depends on the command convert (imageMagick)

import sys
import os
import json


class RConfig(object):
    @staticmethod
    def is_mac():
        if sys.platform == "darwin":
            return True
        return False

    @staticmethod
    def is_linux():
        p = sys.platform
        if p == "linux2" or p == "linux" or p.startswith("linux"):
            return True
        return False

    @staticmethod
    def is_windows():
        p = sys.platform
        if p == 'win32' or p == 'win64' or p.startswith('win'):
            return True
        return False

    @staticmethod
    def setup_path_to_inkscape(path_inkscape):
        path = path_inkscape
        if path_inkscape is None:
            if RConfig.is_mac():
                path = "/Applications/Inkscape.app/Contents/Resources/bin/inkscape"
            if RConfig.is_linux():
                path = "inkscape"
            if RConfig.is_windows():
                exit("Unsupported operating system, please type format c: in the command prompt")
        else:
            path = path_inkscape
        return path

    @staticmethod
    def setup_path_to_convert(path_convert):
        path = path_convert
        if path_convert is None:
            if RConfig.is_mac():
                path = "convert"
            if RConfig.is_linux():
                path = "convert"
            if RConfig.is_windows():
                exit("Unsupported operating system, please type format c: in the command prompt")
        else:
            path = path_convert
        return path


class R(object):

    def __init__(self, path_inkscape=None, path_convert=None):
        self.path_inkscape = RConfig.setup_path_to_inkscape(path_inkscape)
        self.path_convert = RConfig.setup_path_to_convert(path_convert)

    def svg2png(self, width, height, png_file, svg_file, options=None):
        w = width
        h = height

        if not isinstance(width, str):
            w = str(width)
        if not isinstance(height, str):
            h = str(height)

        cmd = self.path_inkscape + ' --without-gui --file="' + svg_file + '"'
        if options is not None:
            cmd = cmd + " " + options
        cmd = cmd + ' --export-png="' + png_file + '" --export-width=' + w + ' --export-height=' + h
        os.system(cmd)

    def xcf2png(self, width, height, out_file, in_file):
        w = width
        h = height

        if not isinstance(width, str):
            w = str(width)
        if not isinstance(height, str):
            h = str(height)

        cmd = self.path_convert + ' "' + in_file + '"'
        cmd = '{} -background transparent -flatten -scale {}x{} "{}"'.format(cmd, w, h, out_file)
        os.system(cmd)

    def xcf2pdf(self, width, height, out_file, in_file):
        w = width
        h = height

        if not isinstance(width, str):
            w = str(width)
        if not isinstance(height, str):
            h = str(height)

        cmd = self.path_convert + ' "' + in_file + '"'
        cmd = '{} -background transparent -flatten -scale {}x{} "{}"'.format(cmd, w, h, out_file)
        os.system(cmd)

    def png2png(self, width, height, out_file, in_file):
        w = width
        h = height

        if not isinstance(width, str):
            w = str(width)
        if not isinstance(height, str):
            h = str(height)

        cmd = self.path_convert + ' ' + in_file
        cmd = '{} -scale {}x{} {}'.format(cmd, w, h, out_file)
        os.system(cmd)

    def png2pngs(self, width2x, height2x, out_file, in_file):
        width1x = width2x / 2
        height1x = height2x / 2
        out_file2x = out_file.replace('.png', '@2x.png')
        self.png2png(width1x, height1x, out_file, in_file)
        self.png2png(width2x, height2x, out_file2x, in_file)

    def xcf2png_r2(self, width2x, height2x, out_file, in_file):
        width1x = width2x / 2
        height1x = height2x / 2
        out_file2x = out_file.replace('.png', '@2x.png')
        self.xcf2png(width1x, height1x, out_file, in_file)
        self.xcf2png(width2x, height2x, out_file2x, in_file)

    def xcf2png_r(self, width1x, height1x, out_file, in_file):
        width2x = width1x * 2
        height2x = height1x * 2
        out_file2x = out_file.replace('.png', '@2x.png')
        self.xcf2png(width1x, height1x, out_file, in_file)
        self.xcf2png(width2x, height2x, out_file2x, in_file)

    def xcf2pngs(self, width1x, height1x, out_file, in_file):
        self.xcf2png_r(width1x, height1x, out_file, in_file)

    def svg2png_r2(self, width2x, height2x, out_file, in_file):
        width1x = width2x / 2
        height1x = height2x / 2
        out_file2x = out_file.replace('.png', '@2x.png')
        self.svg2png(width1x, height1x, out_file, in_file)
        self.svg2png(width2x, height2x, out_file2x, in_file)

    def svg2png_r(self, width1x, height1x, out_file, in_file):
        width2x = width1x * 2
        height2x = height1x * 2
        out_file2x = out_file.replace('.png', '@2x.png')
        self.svg2png(width1x, height1x, out_file, in_file)
        self.svg2png(width2x, height2x, out_file2x, in_file)

    def svg2pngs(self, width1x, height1x, out_file, in_file):
        self.svg2png_r(width1x, height1x, out_file, in_file)

    def svg2icns(self, icon_svg, icon_icns):
        icon_sizes = [16, 32, 32, 64, 128, 256, 256, 512, 512, 1024]
        icon_names = ['16x16', '16x16@2x', '32x32', '32x32@2x', '128x128', '128x128@2x', '256x256', '256x256@2x', '512x512', '512x512@2x']

        tmp_folder = '/tmp/r_icon.iconset/'

        cmd = 'rm -fdr ' + tmp_folder
        os.system(cmd)

        os.mkdir(tmp_folder)

        i = 0
        for icon_size in icon_sizes:
            icon_name = icon_names[i]
            icon_size = str(icon_size)
            self.svg2png(icon_size, icon_size, tmp_folder + 'icon_' + icon_name + '.png', icon_svg)
            i += 1

        cmd = 'iconutil -c icns ' + tmp_folder + ' --output ' + icon_icns
        os.system(cmd)

        cmd = 'rm -fdr ' + tmp_folder
        os.system(cmd)

    def svg2appiconset(self, icon_svg, destination):
        icon_sizes = [(29, "iphone"), (40, "iphone"), (57, "iphone"), (60, "iphone"), (29, "ipad"), (40, "ipad"), (50, "ipad"), (72, "ipad"), (76, "ipad")]

        tmp_root_folder = '/tmp/r_icon.xcassets/'
        tmp_folder = tmp_root_folder + 'AppIcon.appiconset/'

        os.system('rm -fdr ' + tmp_root_folder)

        os.mkdir(tmp_root_folder)
        os.mkdir(tmp_folder)

        d = {"images": [], "info": {"version": 1, "author": "xcode"}}

        images = []
        legacy_names = {"57": "Icon.png", "114": "Icon@2x.png", "72": "Icon-72.png", "144": "Icon-72@2x.png"}
        ban_list = ["iphone-40", "iphone-60"]
        for ics in icon_sizes:

            icon_size = ics[0]
            idiom = ics[1]

            dim_string = "%dx%d" % (icon_size, icon_size)
            wh = icon_size
            wh2 = wh * 2

            if not "%s-%d" % (idiom, icon_size) in ban_list:
                file_name = "icon_%s-%s-1x.png" % (idiom, dim_string)
                if str(wh) in legacy_names:
                    file_name = legacy_names[str(wh)]
                self.svg2png(wh, wh, tmp_folder + file_name, icon_svg)
                images.append({"size": dim_string, "idiom": idiom, "filename": file_name, "scale": "1x"})

            file_name = "icon_%s-%s-2x.png" % (idiom, dim_string)
            if str(wh2) in legacy_names:
                file_name = legacy_names[str(wh2)]
            self.svg2png(wh2, wh2, tmp_folder + file_name, icon_svg)
            images.append({"size": dim_string, "idiom": idiom, "filename": file_name, "scale": "2x"})

        d["images"] = images

        f = file(tmp_folder + 'Contents.json', "w")
        js = json.dumps(d)
        f.write(js)
        f.close()

        dest_folder = os.path.join(destination, 'Images.xcassets')

        if os.path.isdir(dest_folder):
            destination_folder = dest_folder + '/'
            if os.path.isdir(destination_folder + 'AppIcon.appiconset/'):
                os.system('rm -fdr ' + destination_folder + 'AppIcon.appiconset/')
            cmd = "mv %s %s" % (tmp_folder, destination_folder)
            os.system(cmd)
        else:
            cmd = "mv %s %s" % (tmp_root_folder, dest_folder)
            os.system(cmd)

    # TODO: Finish this off, plan is to generate the splash images, then add the svg_centre , centred on top of each one. Svg_centre should not be scaled, but fixed size for all.
    def svg2_launch_image(self, svg_bg, svg_centre, destination):
        icon_sizes = [
            (320, 568, "portrait", "iphone", {"extent": "full-screen", "minimum-system-version": "7.0", "subtype": "retina4"}),
            (320, 480, "portrait", "iphone", {"extent": "full-screen", "minimum-system-version": "7.0"}),
            (320, 568, "portrait", "iphone", {"extent": "full-screen", "subtype": "retina4"}),
            (320, 480, "portrait", "iphone", {"extent": "full-screen"}),
            (768, 1024, "portrait", "ipad", {"extent": "full-screen", "minimum-system-version": "7.0"}),
            (1024, 768, "landscape", "ipad", {"extent": "full-screen", "minimum-system-version": "7.0"}),
            (768, 1004, "portrait", "ipad", {"extent": "to-status-bar"}),
            (1024, 748, "landscape", "ipad", {"extent": "to-status-bar"})
        ]

        tmp_root_folder = '/tmp/r_icon.xcassets/'
        tmp_folder = tmp_root_folder + 'LaunchImage.launchimage/'

        os.system('rm -fdr ' + tmp_root_folder)

        os.mkdir(tmp_root_folder)
        os.mkdir(tmp_folder)

        d = {"images": [], "info": {"version": 1, "author": "xcode"}}

        images = []
        for icon_size in icon_sizes:
            w = icon_size[0]
            h = icon_size[1]
            o = icon_size[2]
            idiom = icon_size[3]
            aux = icon_size[4]
            e = aux["extent"]

            w2 = w * 2
            h2 = h * 2
            dim_string = "%dx%d" % (w, h)

            skip1x = False
            if idiom == "iphone" and (h == 568 or h == 480):
                skip1x = True

            if skip1x is False:
                icon_name = "%s-%s-%s-%s-1x" % (idiom, o, e, dim_string)
                file_name = 'launchimg_' + icon_name + '.png'
                self.svg2png(w, h, tmp_folder + file_name, svg_bg)
                img = {"size": dim_string, "idiom": idiom, "filename": file_name, "scale": "1x", "orientation": o, "extent": e}
                img = dict(img.items() + aux.items())
                images.append(img)

            icon_name = "%s-%s-%s-%s-2x" % (idiom, o, e, dim_string)
            file_name = 'launchimg_' + icon_name + '.png'
            self.svg2png(w2, h2, tmp_folder + file_name, svg_bg)
            img = {"size": dim_string, "idiom": idiom, "filename": file_name, "scale": "2x", "orientation": o, "extent": e}
            img = dict(img.items() + aux.items())
            images.append(img)

        d["images"] = images

        f = file(tmp_folder + 'Contents.json', "w")
        js = json.dumps(d)
        f.write(js)
        f.close()

        dest_folder = os.path.join(destination, 'Images.xcassets')

        if os.path.isdir(dest_folder):
            destination_folder = dest_folder + '/'
            if os.path.isdir(destination_folder + 'LaunchImage.launchimage/'):
                os.system('rm -fdr ' + destination_folder + 'LaunchImage.launchimage/')
            cmd = "mv %s %s" % (tmp_folder, destination_folder)
            os.system(cmd)
        else:
            cmd = "mv %s %s" % (tmp_root_folder, dest_folder)
            os.system(cmd)

    def svg2launchimage(self, launch_svg, destination):
        icon_sizes = [
            (320, 568, "portrait", "iphone", {"extent": "full-screen", "minimum-system-version": "7.0", "subtype": "retina4"}),
            (320, 480, "portrait", "iphone", {"extent": "full-screen", "minimum-system-version": "7.0"}),
            (320, 568, "portrait", "iphone", {"extent": "full-screen", "subtype": "retina4"}),
            (320, 480, "portrait", "iphone", {"extent": "full-screen"}),
            (768, 1024, "portrait", "ipad", {"extent": "full-screen", "minimum-system-version": "7.0"}),
            (1024, 768, "landscape", "ipad", {"extent": "full-screen", "minimum-system-version": "7.0"}),
            (768, 1004, "portrait", "ipad", {"extent": "to-status-bar"}),
            (1024, 748, "landscape", "ipad", {"extent": "to-status-bar"})
        ]

        tmp_root_folder = '/tmp/r_icon.xcassets/'
        tmp_folder = tmp_root_folder + 'LaunchImage.launchimage/'

        os.system('rm -fdr ' + tmp_root_folder)

        os.mkdir(tmp_root_folder)
        os.mkdir(tmp_folder)

        d = {"images": [], "info": {"version": 1, "author": "xcode"}}

        images = []
        for icon_size in icon_sizes:
            w = icon_size[0]
            h = icon_size[1]
            o = icon_size[2]
            idiom = icon_size[3]
            aux = icon_size[4]
            e = aux["extent"]

            w2 = w * 2
            h2 = h * 2
            dim_string = "%dx%d" % (w, h)

            skip1x = False
            if idiom == "iphone" and (h == 568 or h == 480):
                skip1x = True

            if skip1x is False:
                icon_name = "%s-%s-%s-%s-1x" % (idiom, o, e, dim_string)
                file_name = 'launchimg_' + icon_name + '.png'
                self.svg2png(w, h, tmp_folder + file_name, launch_svg)
                img = {"size": dim_string, "idiom": idiom, "filename": file_name, "scale": "1x", "orientation": o, "extent": e}
                img = dict(img.items() + aux.items())
                images.append(img)

            icon_name = "%s-%s-%s-%s-2x" % (idiom, o, e, dim_string)
            file_name = 'launchimg_' + icon_name + '.png'
            self.svg2png(w2, h2, tmp_folder + file_name, launch_svg)
            img = {"size": dim_string, "idiom": idiom, "filename": file_name, "scale": "2x", "orientation": o, "extent": e}
            img = dict(img.items() + aux.items())
            images.append(img)

        d["images"] = images

        f = file(tmp_folder + 'Contents.json', "w")
        js = json.dumps(d)
        f.write(js)
        f.close()

        dest_folder = os.path.join(destination, 'Images.xcassets')

        if os.path.isdir(dest_folder):
            destination_folder = dest_folder + '/'
            if os.path.isdir(destination_folder + 'LaunchImage.launchimage/'):
                os.system('rm -fdr ' + destination_folder + 'LaunchImage.launchimage/')
            cmd = "mv %s %s" % (tmp_folder, destination_folder)
            os.system(cmd)
        else:
            cmd = "mv %s %s" % (tmp_root_folder, dest_folder)
            os.system(cmd)
