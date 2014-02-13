#!/usr/bin/env python

import os
import xmltodict  # sudo easy_install xmltodict
import subprocess


class PackAndroid(object):

    def __init__(self, root, project_folder, project, input_apk, destination, keystore, keystore_alias, apk_name=None, zipalign=None, jarsigner=None, configuration='Release'):

        self.proj_folder = project_folder
        self.project = project
        self.input_apk = input_apk
        self.destination = os.path.expanduser(destination)
        self.configuration = configuration

        self.keystore = keystore
        self.keystore_alias = keystore_alias

        # Name of the final apk
        self.apk_name = apk_name
        if self.apk_name is None and self.keystore_alias is not None:
            self.apk_name = self.keystore_alias.lower()
        if self.apk_name is None:
            projf = os.path.basename(project)
            self.apk_name = projf.replace('.csproj', '')
        self.final_apk = os.path.join(self.destination, "%s-" % self.apk_name)
        self.signed_apk = os.path.join(self.destination, "%s-signed.apk" % self.apk_name)

        self.zipalign = zipalign
        if self.zipalign is None:
            self.zipalign = '/usr/bin/zipalign'

        self.jarsigner = jarsigner
        if self.jarsigner is None:
            self.jarsigner = "/usr/bin/jarsigner"

        self.keystore = os.path.join(root, self.keystore)
        self.project = os.path.join(root, self.project)
        self.proj_folder = os.path.join(root, self.proj_folder)
        self.input_apk = os.path.join(self.proj_folder, self.input_apk)

        if not os.path.exists(self.keystore):
            exit("Failed to locate keystore - " + self.keystore)

        if not os.path.exists(self.zipalign):
            exit("Failed to locate zipalign - " + self.zipalign)

        if not os.path.exists(self.jarsigner):
            exit("Failed to locate jarsigner - " + self.jarsigner)

    def clean(self):
        bin_folder = os.path.join(self.proj_folder, 'bin')
        obj_folder = os.path.join(self.proj_folder, 'obj')
        if os.path.exists(bin_folder):
            print 'Clearing away ' + bin_folder
            os.system('rm -fdr ' + bin_folder)
        if os.path.exists(obj_folder):
            print 'Clearing away ' + obj_folder
            os.system('rm -fdr ' + obj_folder)

    def get_manifest_dictionary(self):
        manifest = os.path.join(self.proj_folder, 'Properties/AndroidManifest.xml')
        if not os.path.exists(manifest):
            exit("Failed to locate AndroidManifest.xml - " + manifest)
        f = file(manifest)
        xml = f.read()
        f.close()
        doc = xmltodict.parse(xml)
        return doc

    def get_build_number(self):
        doc = self.get_manifest_dictionary()
        return doc['manifest']['@android:versionCode']

    def get_version_number(self):
        doc = self.get_manifest_dictionary()
        return doc['manifest']['@android:versionName']

    def set_build_number(self, build_num):
        doc = self.get_manifest_dictionary()
        doc['manifest']['@android:versionCode'] = build_num
        xml = xmltodict.unparse(doc)
        manifest = os.path.join(self.proj_folder, 'Properties/AndroidManifest.xml')
        if not os.path.exists(manifest):
            exit("Failed to locate AndroidManifest.xml - " + manifest)
        f = file(manifest, 'w')
        f.write(xml)
        f.close()

    def set_version_number(self, version):
        doc = self.get_manifest_dictionary()
        doc['manifest']['@android:versionName'] = version
        xml = xmltodict.unparse(doc)
        manifest = os.path.join(self.proj_folder, 'Properties/AndroidManifest.xml')
        if not os.path.exists(manifest):
            exit("Failed to locate AndroidManifest.xml - " + manifest)
        f = file(manifest, 'w')
        f.write(xml)
        f.close()

    def build(self):
        cmd = "xbuild %s /t:SignAndroidPackage /p:Configuration=%s" % (self.project, self.configuration)
        os.system(cmd)
        if not os.path.exists(self.input_apk):
            exit("Failed to build raw apk, i.e. its missing - " + self.input_apk)

    def sign(self):
        subprocess.call([self.jarsigner, "-verbose", "-sigalg", "MD5withRSA", "-digestalg", "SHA1", "-keystore", self.keystore, "-signedjar", self.signed_apk, self.input_apk, self.keystore_alias])
        subprocess.call([self.zipalign, "-f", "-v", "4", self.signed_apk, self.final_apk])
        if os.path.exists(self.final_apk):
            if os.path.exists(self.signed_apk):
                os.system('rm ' + self.signed_apk)

    def update_version(self):
        build_number = self.get_build_number()
        print build_number
        q = raw_input("Would you like to increment the build number for %s? y/n\n> " % self.apk_name)
        if q == "y":
            build_number = str(int(build_number)+1)
            self.set_build_number(build_number)

        version_number = self.get_version_number()
        print version_number
        q = raw_input("Would you like to change the version number for %s? y/n\n> " % self.apk_name)
        if q == "y":
            version_number = raw_input("What to?> ")
            self.set_version_number(version_number)

    def run(self, update_versions=True, confirm_build=True):

        self.clean()

        self.final_apk = os.path.join(self.destination, "%s-" % self.apk_name)

        if update_versions:
            self.update_version()

        build_number = self.get_build_number()
        version_number = self.get_version_number()

        if confirm_build:
            print 'So thats version ' + version_number + " build " + build_number
            q = raw_input("Would you like to continue? y/n\n> ")
            if q != "y":
                print "Ok, not doing the build, suit yourself..."
                return None

        self.final_apk = self.final_apk + build_number + '.apk'

        print self.final_apk

        self.build()

        self.sign()

        return self.final_apk
