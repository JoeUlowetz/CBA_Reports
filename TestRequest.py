#-------------------------------------------------------------------------------
# Name:        TestRequest
# Purpose:
#
# Author:      W510
#
# Created:     29/12/2017
# Copyright:   (c) W510 2017
# Licence:     <your licence>
#
#To prepare:
#   (run as admin?)
#   pip install requests
#   pip install BeautifulSoup4
#   pip install lxml
#-------------------------------------------------------------------------------

import requests
from bs4 import BeautifulSoup as bs

def main():
    pass

if __name__ == '__main__':
    main()




def get_login_token(raw_resp):
    soup = bs(raw_resp.text, 'lxml')
    print "LXML:"
    print soup
    print "-----"
    token = [n['value'] for n in soup.find_all('input')
             if n['name'] == 'wpLoginToken']
    return token[0]

payload = {
    'wpName': 'my_username',
    'wpPassword': 'my_password',
    'wpLoginAttempt': 'Log in',
    #'wpLoginToken': '',
    }

with requests.session() as s:
    print "Point 1"
    #resp = s.get('http://en.wikipedia.org/w/index.php?title=Special:UserLogin')
    resp = s.get('https://www.aavso.org/vsx/index.php?view=search.top')

    print "Point 1a"
    print resp
    payload['wpLoginToken'] = get_login_token(resp)

    response_post = s.post('http://en.wikipedia.org/w/index.php?title=Special:UserLogin&action=submitlogin&type=login',
                           data=payload)
    response = s.get('http://en.wikipedia.org/wiki/Special:Watchlist')
    print "Point 2"
    print response