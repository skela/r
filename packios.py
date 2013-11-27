#!/usr/bin/env python

import os


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
        print plist

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