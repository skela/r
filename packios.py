#!/usr/bin/env python

import os
import plistlib


class PackIOS(object):

    def __init__(self, root, proj_folder, project, solution, mdtool=None):
        self.mdtool = mdtool
        self.proj_folder = os.path.join(root, proj_folder)
        self.project = os.path.join(root, project)
        self.solution = os.path.join(root, solution)
        self.project_bin = os.path.join(root, proj_folder, 'bin/iPhone/Ad-Hoc')

        if self.mdtool is None:
            self.mdtool = "/Applications/Xamarin Studio.app/Contents/MacOS/mdtool"

        if not os.path.exists(self.mdtool):
            exit("Failed to locate mdtool - " + self.mdtool)

    def name_of_file(self,file_type):
        files = os.listdir(self.project_bin)
        ipa_files = []
        for f in files:
            if f.endswith('.'+file_type):
                ipa_files.append(f)
        if len(ipa_files) > 1:
            exit("Too many %s files, not sure which one to pick" % file_type)
        if len(ipa_files) == 0:
            exit("Failed to find %s file" % file_type)
        ipa = ipa_files[0]
        return ipa

    def name_of_ipa(self):
        return self.name_of_file('ipa')

    def name_of_dsym(self):
        return self.name_of_file('dSYM')

    def path_to_ipa(self):
        name = self.name_of_ipa()
        return os.path.join(self.project_bin, name)

    def path_to_dsym(self):
        name = self.name_of_dsym()
        return os.path.join(self.project_bin, name)

    def path_to_info_plist(self):
        return os.path.join(self.proj_folder, 'Info.plist')

    def get_build_number(self):
        plist = self.path_to_info_plist()
        k = plistlib.readPlist(plist)
        if 'CFBundleVersion' in k:
            return k['CFBundleVersion']
        return None

    def set_build_number(self, build_num):
        plist = self.path_to_info_plist()
        k = plistlib.readPlist(plist)
        k['CFBundleVersion'] = build_num
        plistlib.writePlist(k, plist)

    def get_version_number(self):
        plist = self.path_to_info_plist()
        k = plistlib.readPlist(plist)
        if 'CFBundleShortVersionString' in k:
            return k['CFBundleShortVersionString']
        return None

    def set_version_number(self, version_num):
        plist = self.path_to_info_plist()
        k = plistlib.readPlist(plist)
        k['CFBundleShortVersionString'] = version_num
        plistlib.writePlist(k, plist)

    def clean(self):
        bin_folder = os.path.join(self.proj_folder, 'bin')
        obj_folder = os.path.join(self.proj_folder, 'obj')
        if os.path.exists(bin_folder):
            print 'Clearing away ' + bin_folder
            os.system('rm -fdr ' + bin_folder)
        if os.path.exists(obj_folder):
            print 'Clearing away ' + obj_folder
            os.system('rm -fdr ' + obj_folder)

    def build(self, verbosely=False):
        v = ""
        if verbosely:
            v = "-v"
        cmd = '"%s" %s build "--configuration:Ad-Hoc|iPhone" "%s"' % (self.mdtool, v, self.solution)
        os.system(cmd)
        if not os.path.exists(self.path_to_ipa()):
            exit("Failed to build ipa, i.e. its missing - " + self.path_to_ipa())

    def update_version(self):
        print '=>Update version information for ' + os.path.basename(self.project)
        build_number = self.get_build_number()
        print build_number
        msg = "Would you like to increment the build number? y/n\n> "
        if build_number is None:
            msg = "Has no build number, would you like to start one? y/n\n>"
        q = raw_input(msg)
        if q == "y":
            if build_number is None:
                build_number = "1"
            else:
                build_number = str(int(build_number)+1)
            self.set_build_number(build_number)

        version_number = self.get_version_number()
        print version_number
        msg = "Would you like to change the version number? y/n\n> "
        if version_number is None:
            msg = "Has no version number, would you like to set one? y/n\n>"
        q = raw_input(msg)
        if q == "y":
            version_number = raw_input("What to?> ")
            self.set_version_number(version_number)

    def run(self, update_versions=True, confirm_build=True):
        self.clean()

        if update_versions:
            self.update_version()

        build_number = self.get_build_number()
        version_number = self.get_version_number()

        if build_number is None:
            build_number = "[Missing]"
        if version_number is None:
            version_number = "[Missing]"

        if confirm_build:
            print 'So thats version ' + version_number + " build " + build_number
            q = raw_input("Would you like to continue? y/n\n> ")
            if q != "y":
                print "Ok, not doing the build, suit yourself..."
                return

        self.build()
