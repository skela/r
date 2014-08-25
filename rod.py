
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
        return None

    @staticmethod
    def regenerate_resources(input_folder, output_folder):
        ri = RiOS(output_folder)
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
    def update():
        folder_path = os.curdir
        if folder_path == '.':
            folder_path = os.path.abspath(folder_path)
        xcodeproj = Rod.locate_xcodeproject_file(folder_path)
        if xcodeproj is None:
            exit("Failed to locate xcode project - i.e. Missing .xcodeproj file in folder %s " % folder_path)
        img_folder = Rod.locate_image_resources_folder(xcodeproj)
        if img_folder is None:
            exit("Failed to locate xcode resources/images folder")
        input_folder = Rod.locate_input_resources_folder(folder_path)
        if input_folder is not None:
            Rod.regenerate_resources(input_folder, img_folder)
        Rod.update_xcode_project(xcodeproj, img_folder)

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--init', help="Generate a Rodfile for the current directory.", action='store_true', default=False)
parser.add_argument('-u', '--update', help="Regenerate resources and update the Xcode project", action='store_true', default=False)
args = parser.parse_args()

if args.init:
    Rod.init()
elif args.update:
    Rod.update()
else:
    parser.print_help()
