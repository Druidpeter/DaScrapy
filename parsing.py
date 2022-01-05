import subprocess
import re

from html.parser import HTMLParser

usernameRegEx = re.compile(".com/(.+)/(art|journal|status-update)/")
usernameRegEx_st = re.compile(".com/(.+)/status-update/")
commentRegEx = re.compile("/[0-9]+/([0-9]+)/$")
incRegEx = re.compile("-([0-9]+)$")

class ScrapyParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tagStack = []
        self.outData = []
        self.maxOutData = 10000
        
        self.username = ""
        self.pageDate = ""
        self.urlType = ""
        self.gl_inc = ""
        self.pageUrl = ""
        
    def handle_starttag(self, tag, attrs):
        last_index = len(self.tagStack) - 1
        
        if last_index >= 0:
            enclosing_tag = self.tagStack[last_index]
        else:
            enclosing_tag = False

        if tag == "time" and enclosing_tag == "span":
            for attr in attrs:
                self.pageDate = (attr[1].split("T", 1))[0]
                break

        # After this point, we should have gotten the proper
        # date. Next, look through the html for additional journal,
        # deviation, and status update links.

        if tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    if usernameRegEx.search(attr[1]) != None:
                        self.outData.append(attr[1])
            
        if tag == "a" or tag == "span":
            self.tagStack.append(tag)

    def handle_endtag(self, tag):
        # pop last tag from stack.
        if tag == "a" or tag == "span":
            self.tagStack.pop()

    def fillFromUrl(self, url):
        self.pageUrl = url
        
        if url.count("/art/") > 0:
            # Deviation
            self.urlType = "deviation"
            self.gl_inc = incRegEx.search(url).group(1)
            self.username = usernameRegEx.search(url).group(1)
        elif url.count("/journal/") > 0:
            # Journal
            self.urlType = "journal"
            self.gl_inc = incRegEx.search(url).group(1)
            self.username = usernameRegEx.search(url).group(1)
        elif url.count("/status-update/") > 0:
            # Status Update
            self.urlType = "status"
            self.gl_inc = incRegEx.search(url).group(1)
            self.username = usernameRegEx_st.search(url).group(1)            
    # We should return a list of 6-element lists, each containing a
    # username, wgotten url, date, urlType, urlAssoc, and global
    # increment number. Some of these values, such as date and
    # urlAssoc, will not be valid, and so will have a placeholder
    # False value.
    
    def proc(self, url):
        self.fillFromUrl(url)
        htmlData = subprocess.run(['wget', '-O', '-', url], capture_output=True, text=True)

        self.feed(htmlData.stdout)

        if len(self.outData) > self.maxOutData:
            self.outData = self.outData[:self.maxOutData]
        
        returnData = [[
            self.username,
            self.pageUrl,
            self.pageDate,
            self.urlType,
            self.gl_inc
        ], self.outData]

        dataLog = open("parsing_log.txt", "a")
        dataLog.write(' '.join(str(e) for e in returnData[0]))
        dataLog.write(' '.join(str(e) for e in returnData[1]))
        dataLog.close()
        
        return (returnData)
