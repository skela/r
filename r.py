# Utility Class to create resource recipes for image resources in iOS and Android Projects.
#
# svg2png - Depends on Inkscape
# xcf2png - Depends on the command convert (imageMagick)
# svg2pdf - Depends on svg2pdf

import sys
import os
import json
from decimal import Decimal


class RUtils(object):

    @staticmethod
    def number_from_object(o):
        num = o
        if isinstance(o, str) or isinstance(o, unicode):
            num = Decimal(o)
        return num

    @staticmethod
    def html_color_to_rgb(colorstring):
        """ convert #RRGGBB to an (R, G, B) string used in things like css and other stuff """
        colorstring = colorstring.strip()
        if colorstring[0] == '#': colorstring = colorstring[1:]
        if len(colorstring) != 6:
            raise ValueError, "input #%s is not in #RRGGBB format" % colorstring
        r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
        r, g, b = [int(n, 16) for n in (r, g, b)]
        return "(%d,%d,%d)" % (r, g, b)


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
                if not os.path.exists(path):
                    path = "/opt/local/bin/inkscape"
                if not os.path.exists(path):
                    path = "/usr/local/bin/inkscape"
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

        if not os.path.exists(path):
            path = "/opt/local/bin/convert"
        if not os.path.exists(path):
            path = "/usr/local/bin/convert"

        return path

    @staticmethod
    def setup_path_to_svg2pdf(path_svg2pdf):
        path = path_svg2pdf
        if path_svg2pdf is None:
            if RConfig.is_mac():
                path = "svg2pdf"
            if RConfig.is_linux():
                path = "svg2pdf"
            if RConfig.is_windows():
                exit("Unsupported operating system, please type format c: in the command prompt")
        else:
            path = path_svg2pdf
        return path


class R(object):

    def __init__(self, path_inkscape=None, path_convert=None, path_svg2pdf=None):
        self.path_inkscape = RConfig.setup_path_to_inkscape(path_inkscape)
        self.path_convert = RConfig.setup_path_to_convert(path_convert)
        self.path_svg2pdf = RConfig.setup_path_to_svg2pdf(path_svg2pdf)

    def add_png_to_png(self, png_file1, png_file2, png_file_result=None):
        result = png_file_result
        if result is None:
            result = png_file2

        cmd = self.path_convert
        cmd = cmd.replace("convert", "composite")
        cmd = "%s -gravity center -compose src-over %s %s %s" % (cmd, png_file1, png_file2, result)
        print cmd
        os.system(cmd)

    def svg2png(self, width, height, png_file, svg_file, options=None):
        w = width
        h = height

        if not isinstance(width, str):
            w = str(width)
        if not isinstance(height, str) and h is not None:
            h = str(height)

        svg_path = os.path.abspath(svg_file)
        png_path = os.path.abspath(png_file)

        cmd = self.path_inkscape + ' --without-gui --file="%s"' % svg_path
        cmd += " --export-background-opacity=0"
        if options is not None:
            cmd = cmd + " " + options
        if h is None:
            cmd = cmd + ' --export-png="' + png_path + '" --export-width=' + w
        else:
            cmd = cmd + ' --export-png="' + png_path + '" --export-width=' + w + ' --export-height=' + h
        os.system(cmd)

        return png_path

    def svg2pdf(self, svg_file, pdf_file):
        # cmd = self.path_svg2pdf + " %s %s" % (svg_file, pdf_file)
        cmd = self.path_inkscape + ' --without-gui --file="%s" --export-background-opacity=0 --export-pdf="%s"' % (svg_file, pdf_file)
        os.system(cmd)
        return pdf_file

    def xcf2png(self, width, height, out_file, in_file):
        w = width
        h = height

        if not isinstance(width, str):
            w = str(width)
        if not isinstance(height, str):
            h = str(height)

        in_file = os.path.abspath(in_file)
        out_file = os.path.abspath(out_file)

        cmd = self.path_convert + ' "' + in_file + '"'
        cmd = '{} -background transparent -flatten -scale {}x{} "{}"'.format(cmd, w, h, out_file)
        os.system(cmd)
        return out_file

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

        in_file = os.path.abspath(in_file)
        out_file = os.path.abspath(out_file)

        cmd = self.path_convert + ' ' + in_file
        cmd = '{} -scale {}x{} {}'.format(cmd, w, h, out_file)
        os.system(cmd)
        return out_file

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

    def xcf2png_r(self, w1x, h1x, out_file, in_file):
        width1x = RUtils.number_from_object(w1x)
        height1x = RUtils.number_from_object(h1x)
        width2x = width1x * 2
        height2x = height1x * 2
        out_file2x = out_file.replace('.png', '@2x.png')

        width3x = width1x * 3
        if height1x is not None:
            height3x = height1x * 3
        out_file3x = out_file.replace('.png', '@3x.png')

        paths = list()
        paths.append(self.xcf2png(width1x, height1x, out_file, in_file))
        paths.append(self.xcf2png(width2x, height2x, out_file2x, in_file))
        paths.append(self.xcf2png(width3x, height3x, out_file3x, in_file))
        return paths

    def xcf2pngs(self, width1x, height1x, out_file, in_file):
        return self.xcf2png_r(width1x, height1x, out_file, in_file)

    def svg2png_r2(self, width2x, height2x, out_file, in_file):
        width1x = width2x / 2
        height1x = height2x / 2
        out_file2x = out_file.replace('.png', '@2x.png')
        self.svg2png(width1x, height1x, out_file, in_file)
        self.svg2png(width2x, height2x, out_file2x, in_file)

    def svg2png_r(self, w1x, h1x, out_file, in_file):
        width1x = RUtils.number_from_object(w1x)
        height1x = RUtils.number_from_object(h1x)

        height2x = None
        height3x = None

        width2x = width1x * 2
        if height1x is not None:
            height2x = height1x * 2
        out_file2x = out_file.replace('.png', '@2x.png')

        width3x = width1x * 3
        if height1x is not None:
            height3x = height1x * 3
        out_file3x = out_file.replace('.png', '@3x.png')

        res = list()
        res.append(self.svg2png(width1x, height1x, out_file, in_file))
        res.append(self.svg2png(width2x, height2x, out_file2x, in_file))
        res.append(self.svg2png(width3x, height3x, out_file3x, in_file))
        return res

    def svg2pngs(self, width1x, height1x, out_file, in_file):
        return self.svg2png_r(width1x, height1x, out_file, in_file)

    def png2pngs_r(self, w1x, h1x, out_file, in_file):
        width1x = RUtils.number_from_object(w1x)
        height1x = RUtils.number_from_object(h1x)

        if height1x is None:
            height1x = width1x

        height2x = None
        height3x = None

        width2x = width1x * 2
        if height1x is not None:
            height2x = height1x * 2
        out_file2x = out_file.replace('.png', '@2x.png')

        width3x = width1x * 3
        if height1x is not None:
            height3x = height1x * 3
        out_file3x = out_file.replace('.png', '@3x.png')

        res = list()
        res.append(self.png2png(width1x, height1x, out_file, in_file))
        res.append(self.png2png(width2x, height2x, out_file2x, in_file))
        res.append(self.png2png(width3x, height3x, out_file3x, in_file))
        return res

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
        icon_sizes = [(29, "iphone"), (40, "iphone"), (57, "iphone"), (60, "iphone"), (29, "ipad"), (40, "ipad"), (50, "ipad"), (72, "ipad"), (76, "ipad"), (83.5, "ipad")]
        banlist1x = [(83.5, "ipad")]
        banlist3x = [(57, "iphone"), (29, "ipad"), (40, "ipad"), (50, "ipad"), (72, "ipad"), (76, "ipad"), (83.5, "ipad")]

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

            if Decimal(icon_size)._isinteger():
                dim_string = "%dx%d" % (icon_size, icon_size)
            else:
                dim_string = "%gx%g" % (icon_size, icon_size)
            wh = icon_size
            wh2 = wh * 2
            wh3 = wh * 3

            if ics not in banlist1x:
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

            file_name = "icon_%s-%s-3x.png" % (idiom, dim_string)
            if ics not in banlist3x:
                self.svg2png(wh3, wh3, tmp_folder + file_name, icon_svg)
                images.append({"size": dim_string, "idiom": idiom, "filename": file_name, "scale": "3x"})

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

    def svg2launch_image(self, svg_bg, svg_centred, svg_centred_size_1x, destination, for_iphone=True, for_ipad=True):

        icon_sizes = list()

        if for_iphone:
            ics = [
                (320, 568, "portrait", "iphone", {"extent": "full-screen", "minimum-system-version": "7.0", "subtype": "retina4"}),
                (320, 480, "portrait", "iphone", {"extent": "full-screen", "minimum-system-version": "7.0"}),
                (320, 568, "portrait", "iphone", {"extent": "full-screen", "subtype": "retina4"}),
                (320, 480, "portrait", "iphone", {"extent": "full-screen"}),
            ]
            icon_sizes.extend(ics)

        if for_ipad:
            icsp = [
                (768, 1024, "portrait", "ipad", {"extent": "full-screen", "minimum-system-version": "7.0"}),
                (1024, 768, "landscape", "ipad", {"extent": "full-screen", "minimum-system-version": "7.0"}),
                (768, 1004, "portrait", "ipad", {"extent": "to-status-bar"}),
                (1024, 748, "landscape", "ipad", {"extent": "to-status-bar"})
            ]
            icon_sizes.extend(icsp)

        tmp_root_folder = '/tmp/r_icon.xcassets/'
        tmp_folder = tmp_root_folder + 'LaunchImage.launchimage/'

        os.system('rm -fdr ' + tmp_root_folder)

        os.mkdir(tmp_root_folder)
        os.mkdir(tmp_folder)

        logo_img_1x = self.svg2png(svg_centred_size_1x[0], svg_centred_size_1x[1], tmp_folder + 'logo1.png', svg_centred)
        logo_img_2x = self.svg2png(svg_centred_size_1x[0]*2, svg_centred_size_1x[1]*2, tmp_folder + 'logo2.png', svg_centred)

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
                the_img = self.svg2png(w, h, tmp_folder + file_name, svg_bg)
                self.add_png_to_png(logo_img_1x, the_img)
                img = {"size": dim_string, "idiom": idiom, "filename": file_name, "scale": "1x", "orientation": o, "extent": e}
                img = dict(img.items() + aux.items())
                images.append(img)

            icon_name = "%s-%s-%s-%s-2x" % (idiom, o, e, dim_string)
            file_name = 'launchimg_' + icon_name + '.png'
            the_img = self.svg2png(w2, h2, tmp_folder + file_name, svg_bg)
            self.add_png_to_png(logo_img_2x, the_img)
            img = {"size": dim_string, "idiom": idiom, "filename": file_name, "scale": "2x", "orientation": o, "extent": e}
            img = dict(img.items() + aux.items())
            images.append(img)

        os.remove(logo_img_1x)
        os.remove(logo_img_2x)

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

    def svg2launch_image_iphone(self, svg_bg, svg_centred, svg_centred_size_1x, destination):
        self.svg2launch_image(svg_bg, svg_centred, svg_centred_size_1x, destination, for_iphone=True, for_ipad=False)

    def svg2launch_image_ipad(self, svg_bg, svg_centred, svg_centred_size_1x, destination):
        self.svg2launch_image(svg_bg, svg_centred, svg_centred_size_1x, destination, for_iphone=False, for_ipad=True)

    # Note this is not that useful, you may want to make use of the svg2launch_image function above.
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

    def svg2android_icons(self, svg_file, target):
        icon_sizes = [
            (36, 36, "drawable-ldpi"),
            (48, 48, "drawable-mdpi"),
            (72, 72, "drawable-hdpi"),
            (96, 96, "drawable-xhdpi"),
            (144, 144, "drawable-xxhdpi"),
            (192, 192, "drawable-xxxhdpi")
        ]

        resources_folder = target
        icon_name = 'ic_launcher.png'
        if target.endswith('.png'):
            icon_name = os.path.basename(target)
            resources_folder = resources_folder.replace(icon_name, '')

        tmp_root_folder = '/tmp/r_icons.droid/'
        os.system('rm -fdr ' + tmp_root_folder)
        os.mkdir(tmp_root_folder)

        for icon_size in icon_sizes:
            w = icon_size[0]
            h = icon_size[1]
            o = icon_size[2]
            p = os.path.join(tmp_root_folder, o)
            os.mkdir(p)
            png_file = os.path.join(p, icon_name)
            self.svg2png(w, h, png_file, svg_file)

        cmd = "cp -R %s %s" % (tmp_root_folder, resources_folder)
        os.system(cmd)

    def convert(self, in_path_png, out_path_png, actions):
        cmd = '%s "%s" %s "%s"' % (self.path_convert, in_path_png, actions, out_path_png)
        os.system(cmd)

    def convert_color(self, in_path_png, out_path_png, from_color, to_color):
        """
        from color is the the color u want to convert - either rgb(51,51,51) or a color name
        to color is the color u want to convert to
        """

        if to_color.startswith("#"):
            to_color = RUtils.html_color_to_rgb(to_color)

        if from_color.startswith("#"):
            from_color = RUtils.html_color_to_rgb(from_color)

        cmd = '%s "%s" +level-colors "%s","%s" "%s"' % (self.path_convert, in_path_png, from_color, to_color, out_path_png)
        os.system(cmd)

    def convert_color_from_white(self, in_path_png, out_path_png, to_color):
        self.convert_color(in_path_png, out_path_png, 'white', to_color)

    def convert_color_from_black(self, in_path_png, out_path_png, to_color):
        self.convert_color(in_path_png, out_path_png, 'black', to_color)

