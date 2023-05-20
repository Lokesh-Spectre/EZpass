'''
ToDo - SSL
Todo - pgp signature (public key private key)
Todo - extension - main connection string by user
extension verification:
one-time-setup
a string (password hashed 21 times) will be given by main GUI
that has to be submitted to extension to connect them
'''

from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime as dt
import json
from PySide6.QtCore import QObject
import os

data = {"github.com": {"user_id": "login_field", "passwd_id": "password"},
        "profile.w3schools.com": {"user_id": "modalusername", "passwd_id": "current-password"},
        "stackoverflow.com": {"user_id": "email", "passwd_id": "password"},
        "quora.com": {"user_id": "email", "passwd_id": "password"},
        "en.wikipedia.org": {"user_id": "wpName1", "passwd_id": "wpPassword1"},
        "users.wix.com": {"user_id": "input_0", "passwd_id": "input_2"},
        "entrepreneur.com": {"user_id": "email", "passwd_id": "password"},
        "website.com": {"user_id": "username", "passwd_id": "password"},
        "amazon.in": {"user_id": "ap_email", "passwd_id": "ap_password"}}

dname = lambda x: x.strip().lstrip('www.')
new = {}
for i in data:
    new[dname(i)] = data[i]
data = new.copy()
del new


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()

        site = self.path[1:]
        siteIds = self.getSiteIds(site)
        pInfo = DBMO.getPublicInfo()
        site = dname(site)
        for i in pInfo:
            print(site, i)
            if site in i and siteIds is not None:
                data = {'username': DBMO.getusr(i),
                        'passwd': DBMO.getpasswd(i),
                        'user_id': siteIds['user_id'],
                        'passwd_id': siteIds['passwd_id'],
                        'found': True}
                break
        else:
            data = {'found': False}

        self.wfile.write(json.dumps(data).encode())

    def getSiteIds(self, site):
        site = dname(site)
        if dname(site) in data:
            return data[site]


class server(QObject):

    def __init__(self, dbmo):
        super(server, self).__init__()
        global DBMO
        DBMO = dbmo

    def run(self):
        httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
        httpd.serve_forever()
