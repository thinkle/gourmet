import urllib.error
import urllib.parse
import urllib.request
import webbrowser

from gourmet.gdebug import debug


class Emailer:
    def __init__ (self, emailaddress=None, subject=None, body=None, attachments=[]):
        self.emailaddress=None
        self.subject=subject
        self.body=body
        self.attachments=attachments
        self.connector_string = "?"

    def send_email (self):
        print('send_email()')
        self.url = "mailto:"
        if self.emailaddress: self.url += self.emailaddress
        if self.subject:
            self.url_append('subject',self.subject)
        if self.body:
            self.url_append('body',self.body)
        for a in self.attachments:
            print('Adding attachment',a)
            self.url_append('attachment',a)
        debug('launching URL %s'%self.url,0)
        webbrowser.open(self.url)

    def url_append (self, attr, value):
        self.url += "%s%s=%s"%(self.connector(),attr,urllib.parse.quote(value.encode('utf-8','replace')))

    def connector (self):
        retval = self.connector_string
        self.connector_string = "&"
        return retval

if __name__ == '__main__':
    e = Emailer(emailaddress='tmhinkle@gmail.com',subject='Hello',body="<html><b>hello</b></html>")
    e.send_email()
