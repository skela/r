#!/usr/bin/env python

import requests
import os.path
import shutil
import json

'''
api_token = The API token from the testflight website.
team_token = The team token from the testflight website.
distribution-lists = The name of the distribution list or lists in testflight which should have access to this build.
should_notify = True if the distribution list should be notified for this build.
notes = Your release notes for this build.
'''


class PackFlightSettings(object):

    def __init__(self, api_token, team_token, distribution_lists=None, should_notify=False, slack_settings=None, notes=""):
        self.api_token = api_token
        self.team_token = team_token
        self.distribution_lists = distribution_lists
        self.should_notify = should_notify
        self.notes = notes
        self.slack_settings = slack_settings


class PackSlackSettings(object):

    def __init__(self, app_name, team, token, channel, username, text, icon_emoji=":ghost:"):
        self.app_name = app_name
        self.team = team
        self.token = token
        self.channel = channel
        self.username = username
        self.text = text
        self.icon_emoji = icon_emoji

    def update_with_tf_results(self, tfd):
        """ tfd looks like this:
            {
            "bundle_version": "1.0.0 (1)",
            "install_url": "someurl",
            "config_url": "someotherurl",
             "created_at": "2014-02-10 09:10:10",
            "notify": false,
            "team": "teamname",
            "minimum_os_version": "8",
            "release_notes": "",
            "binary_size": 9917655
            }
        """
        self.text = "New build of %s [ %s ] - <%s|Config> - <%s|Install>" % (self.app_name, tfd['bundle_version'], tfd['config_url'], tfd['install_url'])


class PackFlightUtils(object):

    @staticmethod
    def is_blank(some_text):
        return some_text is None or some_text == ""

    @staticmethod
    def make_url_request(req_url, params):
        import urllib2
        data = json.dumps(params)
        headers = dict()
        headers['Content-Type'] = 'application/json; charset=utf-8;'
        headers['User-Agent'] = 'urllib2 / python'

        request = urllib2.Request(req_url, data, headers)
        response = None
        try:
            resp = urllib2.urlopen(request)
            response = resp.read()
            print 'Request Finished:'+response
        except Exception, er:
            response['code'] = 1
            response['msg'] = 'Request failed: ' + str(er)
            print 'Request Failed:'+str(er)
        return response


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
        response_text = None
        try:
            req = requests.post(url=self.url, data=params, files=files)
            response_text = req.text
            print response_text
        except Exception, er:
            print "Failed to upload file - %s" % er
        finally:
            if build_is_ios:
                if os.path.exists(dsym_file_zip):
                    #print 'Clearing away ' + dsym_file_zip
                    os.system('rm -fdr ' + dsym_file_zip)

        if response_text is not None:
            if self.settings.slack_settings is not None:
                tf_d = json.loads(response_text)
                self.settings.slack_settings.update_with_tf_results(tf_d)
                ss = self.settings.slack_settings
                payload = {"channel": ss.channel, "username": ss.username, "text": ss.text, "icon_emoji": ss.icon_emoji}
                turl = "https://%s.slack.com/services/hooks/incoming-webhook?token=%s" % (ss.team, ss.token)
                PackFlightUtils.make_url_request(turl, payload)
