#!python2
#-------------------------------------------------------------------------------
# Name:        UploadFiles.py
# Purpose:      Used w/ DownloadWebPage.py for CBA info summary
#
# Author:      Joe Ulowetz
#
# Created:     2017.12.17
# Copyright:   (c) Joe 2017
# Licence:     <your licence>
#
# Warning: must first install library before using this on new computer:
#   pip install --upgrade google-api-python-client
#-------------------------------------------------------------------------------


from __future__ import print_function
import os

#from apiclient import discovery
from googleapiclient.discovery import build

import googleapiclient
from httplib2 import Http
from oauth2client import file, client, tools

#NOT SURE IF I NEED THIS PART:
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

#-------------------------------------------------------------------------------
def UploadFileList(FileList):
    # FileList = list of [filename,mimeType] strings

    SCOPES = 'https://www.googleapis.com/auth/drive.file'
    store = file.Storage('storage.json')
    creds = store.get()

#REMINDER: IF CURRENT storage.json FILE NOT UP TO DATE, THIS OPENS BROWSER AND REQUIRES MANUAL
#INTERVENTION BEFORE IT CAN CONTINUE; THIS SHOULD ONLY BE NECESSARY ONCE ON A COMPUTER
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_id.json', SCOPES)
        creds = tools.run_flow(flow, store)
    #DRIVE = googleapiclient.discovery.build('drive', 'v3', http=creds.authorize(Http()))
    DRIVE = build('drive', 'v3', http=creds.authorize(Http()))

    files = DRIVE.files().list().execute().get('files', []) #gets all my current files in Drive

    for filename, mimeType in FileList:
        #Does this file already exist in Drive? If no then need to create; else need to update
        bExist = False
        id = ""
        for f in files:
            if f['name'] == filename:
                if mimeType:    #if mimetype specified in list, must match Drive entry
                    if f['mimeType'] == mimeType:
                        #print("My id = %s for mimeType=%s" % (f['id'],mimeType))
                        id = f['id']
                        bExist = True
                        break
                    else:
                        continue    #this was not a match; there might be another one
                #else no mimeType to match, so matching name is enough
                #print("My id = %s" % f['id'])
                id = f['id']
                bExist = True
                break
        if bExist:
            #Update
            metadata = {'name':filename}
            res = DRIVE.files().update(fileId=id,body=metadata,media_body=filename).execute()
            if res:
                print('UPDATED existing file: "%s"' % (filename,))
        else:
            #add new file:
            metadata = {'name':filename}
            if mimeType:
                metadata['mimeType'] = mimeType
            res = DRIVE.files().create(body=metadata,media_body=filename).execute()
            #warning: if you get 'Insufficient Permission' here, fix SCOPES string, and delete current storage.json so it will be recreated
            if res:
                print('Uploaded NEW file: "%s" (%s)' % (filename,res['mimeType']))

# NOT QUITE WORKING: NEED TO UPLOAD/UPDATE EXISTING FILE, OTHERWISE I JUST ADD A NEW FILE DOING THIS

#-------------------------------------------------------------------------------
def main(): #testing
    FileList = (
        ('TEST.txt','text/plain'),
        #('hello.txt','application/vnd.google-apps.document'),
        #('CBA_Report1_obs_stars.txt','application/vnd.google-apps.document'),
        #('CBA_Report2_star_obs.txt','application/vnd.google-apps.document'),
        )
    UploadFileList(FileList)

if __name__ == '__main__':
    main()
