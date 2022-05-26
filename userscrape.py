import sys
import math
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from dascrape import getComplexDelay

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 userscrape.py <userlist>")
        exit()

    print("Loading initial Data.")
    fileParam = sys.argv[1]
    initDataFd = open(fileParam, 'r')
    procData = initDataFd.readlines()

    driver = webdriver.Firefox()

    urlPrefix = "https://www.deviantart.com/"
    urlPostfix = "/about"
    
    outDataFd = open('userlist.out.txt', 'w')

    counter = 0
    delayGen = getComplexDelay()
    
    for username in procData:
        print(f"Harvest Cycle: {counter}")
        print(f"Username: {username}")
        counter += 1

        # if counter == 10:
        #     break;
        
        url = urlPrefix + username + urlPostfix
        driver.get(url)

        # Watchers
        # #watchers > button:nth-child(3)

        # Watching
        # #watching > button:nth-child(3)

        # Get the button for loading more watchers.
        try:
            loadMoreWatchers = driver.find_element_by_css_selector(
                '#watchers > button:nth-child(3)')
        except:
            pass

        # Calculate number of watchers on page.
        try:
            numWatchers = driver.find_elements_by_css_selector(
                '#watchers ' + 'div:nth-child(1) ' + 'div:nth-child(2)'
            )

            numWatchers = numWatchers.split(" ")[0]

            if numWatchers[-1] == "K":
                numWatchers = float(numWatchers[0:-1]) * 1000
        except:
            numWatchers = 0

        # Get the button for loading more watched people.
        try:
            loadMoreWatching = driver.find_element_by_css_selector(
                '#watching> button:nth-child(3)')
        except:
            pass

        # Calculate number watched by this user.
        try:
            numWatching = driver.find_elements_by_css_selector(
                '#watching ' + 'div:nth-child(1) ' + 'div:nth-child(2)'
            )

            numWatching = numWatching.split(" ")[0]

            if numWatching[-1] == "K":
                numWatching = float(numWatching[0:-1]) * 1000
        except:
            numWatching = 0

        numClicks = 0
            
        if numWatching > 15 and numWatching < (15+24):
            numClicks = 1
        elif numWatching > (15+24):
            numClicks = math.ceil((numWatching - 15) / 24)

        for i in range(0, numClicks):
            print("Loading More Watching")
            loadMoreWatching.click()
            time.sleep(5)

        try:
            watchingList = driver.find_elements_by_css_selector(
                '#watching ._2QMci'
            )
        except:
            watchingList = []

        numClicks = 0

        if numWatchers > 15 and numWatchers < (15+24):
            numClicks = 1
        elif numWatchers > (15+24):
            numClicks = math.ceil((numWatchers - 15) / 24)

        for i in range(0, numClicks):
            print("Loading More Watchers")
            loadMoreWatchers.click()
            time.sleep(0.5)

            
        try:
            watcherList = driver.find_elements_by_css_selector(
                '#watchers ._2QMci'
            )
        except:
            watcherList = []

        for item in watcherList:
            print("Writing Watchers")
            outDataFd.write(item.get_attribute('innerHTML') + "\n")

        for item in watchingList:
            print("Writing Watching")
            outDataFd.write(item.get_attribute('innerHTML') + "\n")

        time.sleep(next(delayGen))
        print("Harvesting for next User...")

        
        

    outDataFd.close()

if __name__ == "__main__":
    main()
