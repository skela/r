#!/usr/bin/env python

import requests
import os.path
import shutil

'''
api_token = The API token from the testflight website.
team_token = The team token from the testflight website.
distribution-lists = The name of the distribution list or lists in testflight which should have access to this build.
should_notify = True if the distribution list should be notified for this build.
notes = Your release notes for this build.
'''


class PackFlightSettings(object):

    def __init__(self, api_token, team_token, distribution_lists=None, should_notify=False, notes=""):
        self.api_token = api_token
        self.team_token = team_token
        self.distribution_lists = distribution_lists
        self.should_notify = should_notify
        self.notes = notes


class PackFlightUtils(object):

    @staticmethod
    def is_blank(some_text):
        return some_text is None or some_text == ""


class PackFlight(object):

    def __init__(self, settings):
        self.url = 'http://testflightapp.com/api/builds.json'
        self.settings = settings

    '''
    build_file = the path to the ipa or apk file.
    dsym = The .dSYM corresponding to the build.
    '''
    def upload(self, build_file, dsym_file=None):

        if not os.path.exists(build_file):
            exit("Error! %s build file doesn't exist" % build_file)

        build_is_ios = build_file.endswith('.ipa')

        dsym_file_zip = None

        if build_is_ios:
            if PackFlightUtils.is_blank(dsym_file):
                exit("Error! %s dSYM file doesn't exist" % dsym_file)
            dsym_file_zip_name = os.path.basename(dsym_file)
            dsym_file_zip = shutil.make_archive(dsym_file_zip_name, "zip", dsym_file)

        if build_is_ios:
            if PackFlightUtils.is_blank(dsym_file_zip):
                exit("Error! %s dSYM zip file doesn't exist" % dsym_file_zip)

        params = dict()
        params['api_token'] = self.settings.api_token
        params['team_token'] = self.settings.team_token
        params['notify'] = self.settings.should_notify
        params['notes'] = self.settings.notes
        params['distribution_lists'] = self.settings.distribution_lists

        print "Uploading file..."
        files = {'file': open(build_file, 'rb')}
        if build_is_ios and not PackFlightUtils.is_blank(dsym_file_zip):
            files['dsym'] = open(dsym_file_zip, 'rb')
        try:
            req = requests.post(url=self.url, data=params, files=files)
            print req.text
        except Exception, er:
            print "Failed to upload file - %s" % er
        finally:
            if build_is_ios:
                if os.path.exists(dsym_file_zip):
                    #print 'Clearing away ' + dsym_file_zip
                    os.system('rm -fdr ' + dsym_file_zip)
