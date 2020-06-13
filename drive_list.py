from __future__ import print_function
import os

from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

#SCOPES = 'https://www.googleapis.com/auth/drive.readonly.metadata'
SCOPES = 'https://www.googleapis.com/auth/drive.file'
store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_id.json', SCOPES)
    creds = tools.run_flow(flow, store)
DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http()))

files = DRIVE.files().list().execute().get('files', [])
print("len(files) = %d" % len(files) )
for f in files:
    #print(f['name'],f['mimeType'])  #if using v2, this would be 'title' instead of 'name'
    print( f )
    if f['name'] == 'SecondGen.txt':
        print("My id = %s" % f['id'])
