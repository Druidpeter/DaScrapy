import subprocess
import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import WebDriverException

from html.parser import HTMLParser
from db_interface import DB_Interface
from harvester import HarvestDeviationHTML, HarvestGalleryHTML

usernameRegEx = re.compile(".com/(.+)/(art|journal|status-update)/")
usernameRegEx_st = re.compile(".com/(.+)/status-update/")
commentRegEx = re.compile("/[0-9]+/([0-9]+)/$")
incRegEx = re.compile("-([0-9]+)$")

driver = webdriver.Firefox()

db = DB_Interface()

class URLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tagStack = []
        
        self.username = ""
        self.pageDate = False
        self.urlType = ""
        self.gl_inc = ""
        self.pageUrl = ""
        
        self.proc_complete = False
        
    def handle_starttag(self, tag, attrs):
        if(self.proc_complete == True):
            return
        
        last_index = len(self.tagStack) - 1
        
        if last_index >= 0:
            enclosing_tag = self.tagStack[last_index]
        else:
            enclosing_tag = False

        if tag == "time" and enclosing_tag == "span":
            for attr in attrs:
                if attr[0] == "datetime":
                    td = (attr[1].split("T", 1))
                    td[1] = td[1][:8]
                    self.pageDate = td[0] + " " + td[1]
                    self.proc_complete = True
                    break

        if tag == "a" or tag == "span":
            self.tagStack.append(tag)

    def handle_endtag(self, tag):
        if(self.proc_complete == True):
            return
        
        # pop last tag from stack.
        if tag == "a" or tag == "span":
            self.tagStack.pop()
            
    def fillFromUrl(self):
        match_ob = False

        match_ob = incRegEx.search(self.pageUrl)

        if match_ob:
            self.gl_inc = match_ob.group(1)
        else:
            self.urlType = False
            return

        match_ob = usernameRegEx.search(self.pageUrl)

        if match_ob:
            self.username = match_ob.group(1)
        else:
            self.urlType = False
            return
        
        if self.pageUrl.count("/art/") > 0:
            # Deviation
            self.urlType = "deviation"
        elif self.pageUrl.count("/journal/") > 0:
            # Journal
            self.urlType = "journal"
        elif self.pageUrl.count("/status-update/") > 0:
            # Status Update
            self.urlType = "status"
        else:
            self.urlType = False
            
    def proc(self, url):
        # Make sure to reset proc_complete each proc run. This is just
        # an optimization hack.
        self.proc_complete = False
        
        self.pageUrl = url
        self.fillFromUrl()
        
        # Selenium Generator injection point.
        htmlData = HarvestDeviationHTML(self.pageUrl, driver)
        self.feed(htmlData)

        if(self.urlType != False and db.check_url(self.pageUrl) == False):
            print("Inserting into Database: " + self.pageUrl)
            
            db.proc(self.username, self.pageUrl, self.pageDate,
                    self.urlType, self.gl_inc)
            
class URLHarvester(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.outData = []
        
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    if self.isValidUrl(attr[1]) == True:
                        if db.check_url(attr[1]) == False:
                            self.outData.append(attr[1])

    def isValidUrl(self, url):
        if url.count("#") > 0:
            # Not the kind of deviation we're looking for.
            return False
        
        if url.count("/art/") > 0:
            # Deviation
            return True
        elif url.count("/journal/") > 0:
            # Journal
            return True
        elif url.count("/status-update/") > 0:
            # Status Update
            return True
        else:
            return False
            
    def proc(self, url):        
        # Selenium Generator injection point.
        htmlData = HarvestGalleryHTML(url, driver)
        print(htmlData)

        # Parsing using HTMLParser derived objects is now depreciated.
        # Most of the code remains untouched for efficiency reasons.
        # HarvestGalleryHTML now directly returns the urls as a list.
        # self.feed(htmlData)
        
        return htmlData
