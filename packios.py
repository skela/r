#!/usr/bin/env python

import os
import plistlib


class PackIOS(object):

    def __init__(self, root, proj_folder, project, solution, release_notes=None, mdtool=None, configuration="Ad-Hoc"):
        self.name = proj_folder
        self.mdtool = mdtool
        self.proj_folder = os.path.join(root, proj_folder)
        self.project = os.path.join(root, project)
        self.solution = os.path.join(root, solution)
        self.project_bin = os.path.join(root, proj_folder, 'bin/iPhone/%s' % configuration)
        self.fallback_project_bin = os.path.join(root, proj_folder, 'bin/iPhone/%s' % "Release")
        self.configuration = configuration
        self.project_name = os.path.splitext(os.path.basename(project))[0]

        self.release_notes = release_notes
        if release_notes is not None:
            self.release_notes = os.path.join(root, release_notes)

        if self.mdtool is None:
            self.mdtool = "/Applications/Xamarin Studio.app/Contents/MacOS/mdtool"

        if not os.path.exists(self.mdtool):
            exit("Failed to locate mdtool - " + self.mdtool)

        if self.release_notes is not None:
            if not os.path.exists(self.release_notes):
                exit("Failed to locate release notes - %s" % self.release_notes)

    def get_project_bin_folder(self):
        if os.path.exists(self.project_bin):
            return self.project_bin
        return self.fallback_project_bin

    def get_release_notes(self):
        if self.release_notes is None:
            return ""
        f = open(self.release_notes, 'r')
        rn = f.read()
        f.close()
        return rn

    def files_of_type(self, file_type, folder_path=None):
        fpath = folder_path
        if fpath is None:
            fpath = self.get_project_bin_folder()
        files = os.listdir(fpath)        
        ipa_files = []
        for f in files:
            if f.endswith('.'+file_type):
                ipa_files.append(f)        
        return ipa_files

    def name_of_file(self, file_type):
        ipa_files = self.files_of_type(file_type)        
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
        bin_folder = self.get_project_bin_folder()
        ipa_path = os.path.join(bin_folder, name)        
        return ipa_path

    def path_to_ipa_alt(self):
        name = self.name_of_ipa()
        bin_folder = self.get_project_bin_folder()
        ipa_path = os.path.join(bin_folder, name)        
        folders = []
        files = os.listdir(bin_folder)
        for f in files:
            tmp = os.path.join(bin_folder,f)
            if os.path.isdir(tmp):
                folders.append(os.path.join(tmp,name))
        if len(folders) == 1:
            ipa_path = folders[0] 
        return ipa_path

    # This can hopefully be removed once Xamarin fix the bug they introduced in 9.8.0 / 9.8.1
    def dexamarin_ipas(self):
        bin_folder = self.get_project_bin_folder()
        folders = []
        files = os.listdir(bin_folder)        
        for f in files:
            tmp = os.path.join(bin_folder,f)
            if os.path.isdir(tmp):
                folders.append(tmp)        
        counter = 0
        for folder in folders:
            ipa_files = self.files_of_type('ipa',folder)            
            for ipa_name in ipa_files:
                ipa = os.path.join(folder,ipa_name)
                ipa_name = ipa_name.replace(".ipa","%d.ipa" % counter)
                dest = os.path.join(bin_folder,ipa_name)
                cmd = 'mv "%s" "%s"' % (ipa,dest)                
                os.system(cmd)
                counter += 1        

    def path_to_dsym(self):
        name = self.name_of_dsym()
        return os.path.join(self.get_project_bin_folder(), name)

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

    def increment_build_number(self):
        build_number = self.get_build_number()
        if build_number is None:
            build_number = "1"
        else:
            build_number = str(int(build_number)+1)
        self.set_build_number(build_number)

    def decrement_build_number(self):
        build_number = self.get_build_number()
        if build_number is None:
            build_number = "1"
        else:
            build_number = str(int(build_number)-1)
        self.set_build_number(build_number)

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

        cmd_build = '"%s" %s build "--configuration:%s|iPhone" "--project:%s" "%s"' % (self.mdtool, v, self.configuration,self.project_name,self.solution)
        os.system(cmd_build)

        #cmd_archive = '"%s" %s archive "--configuration:%s|iPhone" "--project:%s" "%s"' % (self.mdtool, v, self.configuration,self.project_name,self.solution)                
        #os.system(cmd_archive)

        if len(self.files_of_type('ipa')) == 0:
            self.dexamarin_ipas()

        ipa_path = self.path_to_ipa()        
        if not os.path.exists(ipa_path):
            exit("Failed to build ipa, i.e. its missing - " + ipa_path)

    def update_version(self):
        print '=>Update version information for ' + os.path.basename(self.project)
        build_number = self.get_build_number()
        print build_number
        msg = "Would you like to increment the build number? y/n\n> "
        if build_number is None:
            msg = "Has no build number, would you like to start one? y/n\n>"
        q = raw_input(msg)
        if q == "y":
            self.increment_build_number()

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
