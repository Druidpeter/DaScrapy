import sys
import time
import math
import mariadb

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

from html.parser import HTMLParser

profile = webdriver.FirefoxProfile()
profile.set_preference("browser.cache.disk.enable", False)
profile.set_preference("browser.cache.memory.enable", False)
profile.set_preference("browser.cache.offline.enable", False)
profile.set_preference("network.http.use-cache", False)
driver = webdriver.Firefox(profile)

db_connection = mariadb.connect(
    user="dascrapy_user",
    password="dascrapy_user",
    host="127.0.0.1",
    port=3306,
    database="dascrapy")

session = db_connection.cursor()

def data_cnv(data):
    return data.replace('T', ' ')[:-3]

def main():
    '''Comment Scraping Module'''

    # Get urls from database, and determine if they should be checked
    # for comments.

    session.execute(f"select id from urls order by id desc limit 1;")
    max_id = int(session.fetchone()[0])
    min_id = 0

    if not max_id:
        exit()
    else:
        print(f"Max Id: {max_id}")

    id_checkpoint_fd = open('id_checkpoint.txt', 'r')
    min_id = int(id_checkpoint_fd.readline().strip())
    id_checkpoint_fd.close()
    print(f"Min Id: {min_id}")

    batchsize = 100
    numBatches = 10
    print(f"Setting batch size to: {batchsize}")
    
    while(numBatches > 0):
        if min_id == max_id:
            print("min_id == max_id!! Record Exhaustion. Shutting down.")
            break;

        n_thresh = min(min_id + batchsize, max_id)
        print(f"fetching records using interval: [{min_id}, {n_thresh})")
        
        tmp = getUrlBatch(min_id, n_thresh)
        url_list = [t[0] for t in tmp]
        
        min_id = min(min_id + 100, max_id)
        numBatches -= 1
        
        # if so, send to scrape_comments(url) and receive back the
        # results.  Feed results back into a method which updates the
        # database for each element in the returned results.

        for url in url_list:
            print(f"Scraping comments from URL: {url}")
            results = scrape_comments(url)

            if len(results) == 0:
                continue

            for result in results:
                print(result)
            
            shipToBase(results, url)
            db_connection.commit()

    # Application cleanup and close.
    # Save the last valid min_id to id_checkpoint.txt and print some
    # basic diagnostics information regarding the last run.
    # Then exit.

    with open('id_checkpoint.txt', 'w') as id_checkpoint_fd:
        id_checkpoint_fd.write(str(min_id))
        id_checkpoint_fd.close()

    sys.exit()
    

def getUrlBatch(min_id, max_id):
    session.execute(f"select data from urls where urls.id >= {min_id} and urls.id < {max_id} order by urls.id asc;")

    return session.fetchall()


def shipToBase(results, url):
    print(f"Shipping to Base: {len(results)} results")
    
    for result in results:
        # First, we need to check if the deviant who made the comment is
        # already in the database.

        # If the deviant is not in the database, then we need to add
        # an entry for them, and initialize a ctrl entry for them with
        # last gallery fetched set to epoch time.

        # Finally, we enter the data into the database.
        # ['username','timestamp','href','global_inc']

        query1 = f"select id from deviants where deviants.username like \"{result[0]}\";"
        print(query1)
        session.execute(query1)

        lst_id = session.fetchone()

        if not lst_id:
            query1_1 = ("insert into deviants (username) values "
                        + f" (\"{result[0]}\");")
            
            print(query1_1)
            session.execute(query1_1)
            
            lst_id = session.lastrowid
        
        if(type(lst_id) is tuple):
            lst_id = lst_id[0]

        print(lst_id)

        query2 = f"insert into comments (url_id, deviant_id, commentDate, href, global_inc) values ((select id from urls where urls.data like \"{url}\" limit 1), {lst_id}, \"{result[1]}\", \"{result[2]}\", {result[3]});"

        print(query2)
        session.execute(query2)
    
def scrape_comments(url):
    print(f"scraping from {url}")
    driver.get(url)
    
    # Parse HTML once to determine css selector of load_more button.

    try:
    
        num_comments = driver.find_element_by_css_selector('.eVBLr')
        num_comments = int(num_comments.get_attribute('innerHTML'))

        button = driver.find_element_by_css_selector('._1lBsK._3_MJY._2vim0._1FKeR')

        num_clicks = math.ceil((num_comments - 24)/50)

        # Page loads 24 comments initially,
        # then 50 each click(?).
        
        for i in range(0, num_clicks):
            print("Clicking Load More Comments Button")
            button.click()
            time.sleep(5)

            # Parse HTML a second time to begin harvesting comments.
    
            commentDiv = driver.find_element_by_css_selector('.vJeu0')
            commentHTML = commentDiv.get_attribute('innerHTML')

            commentParser = CommentParser()
            comments = commentParser.proc(commentHTML)

        return comments
    except:
        return []

class LoadMoreCommentsButtonFinder(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tagStack = []
        self.button_css_selector = ""
        self.candidate = ""
        self.num_comments = 0
        self.in_comments_thread = False
        self.in_comments_count = False

    def handle_starttag(self, tag, attrs):
        if tag == "button":
            if self.in_comments_thread:
                for attr in attrs:
                    if attr[0] == "class":
                        self.candidate = "".join((attr[1]).strip())

            self.tagStack.append(tag)

        if tag == "span":
            if self.in_comments_count:
                self.tagStack.append(tag)

        if tag == "div":            
            for attr in attrs:
                if attr[1] == "comments_thread":
                    self.in_comments_thread = True
                    self.tagStack.append(attr[1])
                    break
                elif attr[1] == "comments_count":
                    self.in_comments_count = True
                    self.tagStack.append(attr[1])
                    break

    def handle_data(self, data):
        if len(self.tagStack) <= 0:
            return
        
        if self.in_comments_thread and self.tagStack[-1] == "button":
            if data == "Load More":
                self.button_css_selector = self.candidate    
        elif self.tagStack[-1] == "span" and self.in_comments_count:
            if data.isdigit():
                self.num_comments = int(data)
            

    def handle_endtag(self, tag):
        if len(self.tagStack) <= 0:
            return
        
        if self.tagStack[-1] == "comments_thread":
            self.in_comments_thread = False
        elif self.tagStack[-1] == "comments_count":
            self.in_comments_count = False
        
        if tag == "div" or tag == "button" or tag == "span":
            self.tagStack = self.tagStack[:-1]

    def proc(self):
        self.feed(driver.page_source)
        return self.button_css_selector, self.num_comments
    

class CommentParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tagStack = []
        self.outData = []
        
        self.username = "-1"
        self.timestamp = "-1"
        self.commentUrl = "-1"
        self.global_id = ""

        self.counter = 0
        
        self.inCommentItem = False
        
    def handle_starttag(self, tag, attrs):        
        if tag == "div":
            tagLabel = tag
            
            for attr in attrs:
                if attr[1] == "comments_thread_item":
                    print("Found comments_thread_item")
                    tagLabel = attr[1]
                    self.inCommentItem = True
                    break

            self.tagStack.append(tagLabel)
        
        if (tag == "a" and
            self.inCommentItem == True):
            
            if(self.username == "-1"):
                for attr in attrs:
                    if attr[0] == "data-username":
                        print("Found username")
                        self.username = attr[1]

            if(self.commentUrl == "-1"):
                for attr in attrs:
                    if attr[0] == "href":
                        if(self.counter < 2):
                            self.counter += 1
                        else:
                            print("Found href")
                            self.commentUrl = attr[1]
                            print("Found gloabl_id")
                            self.global_id = attr[1].split('/')[-1]
                            
                            self.counter = 0

        if (tag == "time" and
            self.inCommentItem == True and
            self.timestamp == "-1"):
            for attr in attrs:
                if attr[0] == "datetime":
                    print("Found timestamp")
                    self.timestamp = data_cnv(attr[1])

    def handle_endtag(self, tag):
        if len(self.tagStack) > 0:
            if (tag == "div"):
                if self.tagStack[-1] == "comments_thread_item":
                    print("Leaving comment item")
                    self.inCommentItem = False

                    if (self.username != "-1" and
                        self.timestamp != "-1" and
                        self.commentUrl != "-1"):
                    
                        self.outData.append([self.username,
                                             self.timestamp,
                                             self.commentUrl,
                                             self.global_id])

                    self.username = "-1"
                    self.timestamp = "-1"
                    self.commentUrl = "-1"
                    
                self.tagStack = self.tagStack[:-1]

            
    def proc(self, data):
        print("Feeding HTML Data to parser.")
        self.feed(data)

        for data in self.outData:
            print(data)
        
        return self.outData
    
if __name__ == "__main__":
    main()
