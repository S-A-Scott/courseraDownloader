#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import sys
import random
import urllib
import urllib2
import string
import cookielib
import getpass
from bs4 import BeautifulSoup

user_agent = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36")

postData = urllib.urlencode({
        "email":"charlesgranjor@126.com",
        "password":"zzp19950123",
        "webrequest":"true"
})
class courseraDownloader(object):

    def __init__(self, courseName, email, passwd):
        self.loginUrl = "https://accounts.coursera.org/api/v1/login"
        self.url = "https://class.coursera.org/" + courseName + "/lecture"
        if email == "" or passwd == "":
            print "Invalid email or password"
            sys.exit(2)
        self.email = email
        self.passwd = passwd

    def randomString(self, length):
        return ''.join(random.choice(string.letters + string.digits) for i in xrange(length))

    def construct_headers(self):

        postData = urllib.urlencode({
            "email":self.email,
            "password":self.passwd,
            "webrequest":"true"
        })

        XCSRF2Cookie = 'csrf2_token_%s' % ''.join(self.randomString(8))
        XCSRF2Token = ''.join(self.randomString(24))
        XCSRFToken = ''.join(self.randomString(24))
        cookie = "csrftoken=%s; %s=%s" % (XCSRFToken, XCSRF2Cookie, XCSRF2Token)

        requestHeader = {
                "User-Agent": user_agent,
                "Referer": "https://accounts.coursera.org/signin",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRF2-Cookie": XCSRF2Cookie,
                "X-CSRF2-Token": XCSRF2Token,
                "X-CSRFToken": XCSRFToken,
                "Cookie": cookie
        }

        return postData, requestHeader

    def login(self):
        cookie = cookielib.CookieJar()
        handler = urllib2.HTTPCookieProcessor()
        opener = urllib2.build_opener(handler)
        postData, requestHeader = self.construct_headers()
        urllib2.install_opener(opener)
        req = urllib2.Request("https://accounts.coursera.org/api/v1/login", data = postData, headers = requestHeader)
        try:
            result = urllib2.urlopen(req)
        except urllib2.URLError, e:
            print "Invalid email or password"
            sys.exit(2)

    def getDownloadLinks(self):
        try:
            html = urllib2.urlopen(self.url)
        except urllib2.URLError, e:
            print "Invalid course name"
            sys.exit(2)

        bsObj = BeautifulSoup(html)
        videoLinkList = bsObj.findAll("a", href=re.compile("https://.*\.mp4.*"))
        pdfLinkList = bsObj.findAll("a", href=re.compile("https://.*\.pdf.*"))
        return videoLinkList, pdfLinkList

    def start(self):
        self.login()
        videoLinkList, pdfLinkList = self.getDownloadLinks()
        for video in videoLinkList:
            link = video['href']
            name = video.get_text().replace("Video (MP4) for ", "").replace("\n", "") + ".mp4"
            content = urllib2.urlopen(link).read()
            with open(name, "w") as f:
                f.write(content)
            
        for pdf in pdfLinkList:
            link =  pdf['href']
            #name = pdf.get_text().replace("PDF Slides for ", "")
            os.system("wget " + link)

 
def main():
    if len(sys.argv) != 2:
        print "Usage: ./courseraDownloader.py courseraName"
        sys.exit(2)

    email = raw_input("Enter your account: ")
    passwd = getpass.getpass("Enter your password: ")
    spider = courseraDownloader(sys.argv[1], email, passwd)
    spider.start()


if __name__ == "__main__":
    main()
