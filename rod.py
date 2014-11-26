
import os
import argparse

from r import RiOS


class Rod(object):

    @staticmethod
    def locate_xcodeproject_file(folder_full_path):
        xcodeproj_file_name = None
        files = os.listdir(folder_full_path)
        for f in files:
            if f.endswith(".xcodeproj"):
                xcodeproj_file_name = f
                break
        if xcodeproj_file_name is not None:
            return os.path.join(folder_full_path, xcodeproj_file_name)
        return None

    @staticmethod
    def locate_image_assets_folder(folder_full_path, xcode_project_path):
        res = os.path.join(folder_full_path, 'Images.xcassets')
        if os.path.exists(res):
            if os.path.isdir(res):
                return res
        res = os.path.join(folder_full_path, "Resources", 'Images.xcassets')
        if os.path.exists(res):
            if os.path.isdir(res):
                return res
        name = os.path.basename(xcode_project_path)
        name = name.replace(".xcodeproj", "")
        res = os.path.join(folder_full_path, name, 'Images.xcassets')
        if os.path.exists(res):
            if os.path.isdir(res):
                return res
        res = os.path.join(folder_full_path, name, "Resources", 'Images.xcassets')
        if os.path.exists(res):
            if os.path.isdir(res):
                return res
        return None

    @staticmethod
    def locate_image_resources_folder(xcode_project_path):
        name = os.path.basename(xcode_project_path)
        name = name.replace(".xcodeproj", "")
        root = os.path.split(xcode_project_path)[0]
        code_folder = os.path.join(root, name)
        resources_folder = os.path.join(code_folder, "Resources")
        images_folder = os.path.join(resources_folder, "Images")
        if os.path.exists(code_folder):
            if os.path.isdir(images_folder):
                return images_folder
        return None

    @staticmethod
    def locate_input_resources_folder(folder_full_path):
        res = os.path.join(folder_full_path, 'Resources')
        if os.path.exists(res):
            if os.path.isdir(res):
                return res
        res = os.path.join(folder_full_path, 'Res')
        if os.path.exists(res):
            if os.path.isdir(res):
                return res
        return None

    @staticmethod
    def regenerate_resources(input_folder, output_folder, output_assets_folder):
        ri = RiOS(output_folder)
        ri.set_ios_assets(output_assets_folder)
        ri.run_file("Rodfile", input_folder)

    @staticmethod
    def update_xcode_project(xcodeproj, img_folder):

        pbxproj = os.path.join(xcodeproj, 'project.pbxproj')

        from mod_pbxproj import XcodeProject
        project = XcodeProject.Load(pbxproj)

        groups = project.get_groups_by_name('Images')
        if groups is None or len(groups) == 0:
            exit("XCode group named Images missing")
        if len(groups) > 1:
            exit("Too many groups named 'Images', so bailing'")

        group = groups[0]

        res_files = os.listdir(img_folder)
        for a_file in res_files:
            if a_file.startswith('.'):
                continue
            a_file_path = os.path.join(img_folder, a_file)
            res = project.add_file_if_doesnt_exist(a_file_path, group)
            if len(res) > 0:
                print 'Adding new file - %s' % res

        project.save()

    @staticmethod
    def init():
        folder_path = os.curdir
        if folder_path == '.':
            folder_path = os.path.abspath(folder_path)

        rod_file = os.path.join(folder_path, 'Rodfile')
        if os.path.exists(rod_file):
            if os.path.isfile(rod_file):
                print '[!] Existing Rodfile found in directory'
            else:
                exit("Folder with the name Rodfile detected - This should be a file")
        else:

            c = RiOS.create_run_file_header()
            f = open(rod_file, 'w')
            f.write(c)
            f.close()
            #os.system('touch "%s"' % rod_file)
            print '[*] Rodfile created successfully'

    @staticmethod
    def update():
        (xcodeproj, img_folder, input_folder, assets_folder) = Rod.check(should_print_map=False)
        if input_folder is not None:
            Rod.regenerate_resources(input_folder, img_folder, assets_folder)
        if xcodeproj is not None:
            Rod.update_xcode_project(xcodeproj, img_folder)

    @staticmethod
    def check(should_print_map):
        folder_path = os.curdir
        if folder_path == '.':
            folder_path = os.path.abspath(folder_path)
        xcodeproj = Rod.locate_xcodeproject_file(folder_path)
        if xcodeproj is None:
            print "Failed to locate xcode project - i.e. Missing .xcodeproj file in folder %s\n(So Xcodeproject will not be updated, you have to manually add/remove image resources)" % folder_path
            img_folder = folder_path
        else:
            img_folder = Rod.locate_image_resources_folder(xcodeproj)
        if img_folder is None:
            exit("Failed to locate xcode resources/images folder")
        input_folder = Rod.locate_input_resources_folder(folder_path)
        assets_folder = Rod.locate_image_assets_folder(folder_path, xcodeproj)

        if should_print_map:
            print '> Xcodeproj maps to %s' % xcodeproj
            print '> Image Output folder maps to %s' % img_folder
            print '> Image Assets Output folder maps to %s' % assets_folder
            print '> Res Input folder maps to %s' % input_folder

        return xcodeproj, img_folder, input_folder, assets_folder

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--init', help="Generate a Rodfile for the current directory.", action='store_true', default=False)
parser.add_argument('-u', '--update', help="Regenerate resources and update the Xcode project.", action='store_true', default=False)
parser.add_argument('-c', '--check', help="Check to see if Rod can figure out where the resource inputs and the target outputs are.", action='store_true', default=False)
args = parser.parse_args()

if args.init:
    Rod.init()
elif args.update:
    Rod.update()
elif args.check:
    Rod.check(should_print_map=True)
else:
    parser.print_help()
