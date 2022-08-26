import sys
import random
import time

from html.parser import HTMLParser
from parsing import URLHarvester, URLParser
from collections import OrderedDict
from db_interface import DB_Interface

db = DB_Interface()

def main():    
    '''DeviantArt Scraping Algorithm'''
    # Load a list of usernames and their associated profile urls.

    if len(sys.argv) != 2:
        print("Usage: python3 dascrape.py <userlist>")
        exit()

    print("Loading initial Data.")
    fileParam = sys.argv[1]
    initDataFd = open(fileParam, 'r')
    
    procData = initDataFd.readlines()

    print("Instantiating parser.")
    urlHarvester = URLHarvester()
    urlParser = URLParser()

    urlPrefix = "https://www.deviantart.com/"
    urlPostfix = "/gallery/all"

    urlDataFd = open('lists/urlData.txt', 'a')
    statLogFd = open('lists/statLog.txt', 'a')

    numProcUsers = 0

    
    for username in procData:
        urlDataFd.write("Username: " + username + "\n\n")
        urlDeviations = urlHarvester.proc(urlPrefix + username + urlPostfix)

        # Remove duplicates from urlDeviations
        tmp = list(OrderedDict.fromkeys(urlDeviations))
        urlDeviations = []
        
        # Remove previously inserted deviations.
        for u in tmp:
            if db.check_url(u) == False:
                urlDeviations.append(u)

                
        for url in urlDeviations:
            # Get Complex Delay so as to avoid bot-sniffers.
            random.seed()
            delayGen = getComplexDelay()
            
            urlParser.proc(url)
            urlDataFd.write(url + "\n")

            print("Next Complex Delay: " + str(next(delayGen)) + " seconds.")
            time.sleep(next(delayGen))

        numProcUsers += 1
        urlDataFd.write("Num Procced Users: " + str(numProcUsers) + "\n\n")

    urlDataFd.close()

def testComplexDelay():
    for i in range(1, 1000):
        tmp = getComplexDelay()
        print("Next Complex Delay: " + str(next(tmp)) + " seconds.")
    
def getComplexDelay(timeBase = 10, timeRes = 10000):
    while(True):
        tmp1 = random.randrange(0, timeRes*timeBase)
        tmp2 = random.randrange(0, timeRes*timeBase)

        for i in range(min(tmp1, tmp2), max(tmp1, tmp2)):
            tmp3 = random.randrange(0, timeRes*timeBase + 1)
            tmp4 = random.randrange(0, timeRes*timeBase + 1)
        
            for j in range(min(tmp3, tmp4), max(tmp3, tmp4)):
                anchor = 0.5*i + 0.5*j
                r_mod = 0.2 * anchor + 0.8 * random.randrange(0, timeRes*timeBase + 1)
                r_val = (anchor + (r_mod * random.randrange(-1, 1))) / timeRes

                if r_val < 0:
                    r_val *= -1

                yield r_val
    
if __name__ == "__main__":
    main()
