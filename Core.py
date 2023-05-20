import base64
import pickle

import cryptography
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from datetime import datetime as dt

def keyGen(passwd):
    salt = b'\xc6\xd0B\xbc_\xcf\x14\xdc\xa4\xe0\x036\xd2\xcb\xa8)'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )
    return base64.urlsafe_b64encode(kdf.derive(passwd.encode()))


class DataBaseClass:
    def __init__(self, file_path, passwd=None):

        self.DataB = dict()
        self.isvalid = False
        self.crypt = None
        self.file_path = file_path
        if passwd:
            self.validate(passwd)

    def encrypt(self, data):
        return self.crypt.encrypt(data.encode())


    def decrypt(self, data):
        return self.crypt.decrypt(data).decode()

    def validate(self, passwd):
        key = keyGen(passwd)
        try:
            self.crypt = Fernet(key)
            self.loadDB()  # loadDB poses an error if the password is invalid
            self.isvalid = True

            return True
        except cryptography.fernet.InvalidToken:
            self.isvalid = False
            self.crypt = None
            return False
# {'www.site.com':{'username':<user>,'password':password}}
    def loadDB(self, file_path=None):
        if file_path:
            self.file_path = file_path

        with open(self.file_path, 'rb') as fh:
            raw = self.crypt.decrypt(fh.read())

        self.DataB = pickle.loads(raw)

    def dumpDB(self, file_path=None):
        if not file_path:
            file_path = self.file_path
        data = pickle.dumps(self.DataB)

        with open(file_path, 'wb') as fh:
            fh.write(self.crypt.encrypt(data))

    def getusr(self, site):
        return self.DataB[site]['username']

    def getpasswd(self, site):
        return self.decrypt(self.DataB[site]['password'])

    def getPublicInfo(self):
        PublicInfo = {}
        for i in self.DataB:
            PublicInfo[i] = self.DataB[i]['username']  # {<site_name>:<user_name>}
        return PublicInfo

    def setCred(self, site, username=None, password=None):
        # if Creds for site exists, it replaces only the necessary informations
        site=site.lower().strip()
        if site not in self.DataB:
            credSet = {'username': username, 'password': self.encrypt('')}
            self.DataB[site] = credSet

        if username is not None:
            self.DataB[site]['username'] = username
        if password is not None:
            self.DataB[site]['password'] = self.encrypt(password)

    def createDB(self, passwd, file_path=None):
        if file_path:
            self.file_path = file_path
        self.crypt = Fernet(keyGen(passwd))
        self.dumpDB()
        self.isvalid = True

    def changeSite(self, old_site, new_site):
        new_site=new_site.lower().strip()
        self.DataB[new_site] = self.DataB.pop(old_site)

    def importFromCsv(self,filepath):
        with open(filepath) as f:
            data=[x.split(',') for x in f.read().split('\n')] # csv to 2D list
        del data[0]
        for i in data:
            try:
                self.setCred(i[0],i[2],i[3])
            except IndexError:
                continue
        self.dumpDB()

    def delSite(self,site):
        del self.DataB[site]
