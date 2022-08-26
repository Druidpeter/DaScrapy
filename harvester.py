import time
import re
import sys

#from selenium import webdriver
#from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import WebDriverException

class DoubleDriverException(Exception):
    pass

def HarvestDeviationHTML(url, driver):
    counter = 0
    
    while True:
        try:
            driver.get(url)
            return driver.page_source
        except WebDriverException:
            # I suspect WebDriverException happens because someone
            # server-side terminates our connection, thinking we're a
            # bot. Wait 5 minutes before trying again, and then terminate
            # gracefully if it still doesn't work.

            if counter > 1:
                print("Webdriver failed twice in a row. Aborting processing.")
                raise DoubleDriverException

            print("WebDriverException encountered. Cooling off for 5 minutes...")
            time.sleep(60*5) # Sleep for 5 minutes
            
            counter += 1
            continue

# We need to re-implement the original stack functionality, so that we
# only harvest urls underneath divs of class="_1jrTL"

# Instead of returning the html, return hrefs under divs of
# class="_1jrTL" directly.
def HarvestGalleryHTML(url, driver):
    ckpt = 0
    rlst = []

    print("Creating Webdriver using Firefox Backend")
    print("Accessing Driver URL")
    
    while(ckpt != -1):
        ckpt, hrefs = HarvestGalleryHTML_Inner(url, driver, ckpt, 30)
        print(hrefs)
        rlst.extend(hrefs)
        
    return rlst


def HarvestGalleryHTML_Inner(url, driver, ckpt, bsize):
    lnStrEx = "(https://www\\.deviantart\\.com/.+/art/.+)\" "
    lnRegEx = re.compile(lnStrEx)
    limitRegEx = re.compile("page=(.+)")

    if ckpt == 0:
        driver.get(url)
    else:
        driver.get(url + "?page=" + str(ckpt))

    hrefs = []
    hrefs_el = driver.find_elements_by_css_selector('.RMUi2 a')

    for item in hrefs_el:
        hrefs.append(item.get_attribute("href"))

    tmp2 = len(hrefs)
    print(hrefs)

    print("Calculating additional harvest cycles.")
    elements = driver.find_elements_by_css_selector('a._1qdQj')
    
    if elements:
        links = [elem.get_attribute('href') for elem in elements]

        index_loc = len(links) - 2
        pageLimit = int(limitRegEx.search(links[index_loc]).group(1))

        print("Harvesting relevant URLs from additional Link cycles")
        
        endLoop = min(pageLimit, ckpt + bsize)
        if endLoop == pageLimit:
            rval = -1
        else:
            rval = ckpt + bsize + 1

            
        for i in range(ckpt, endLoop + 1): 
            nextUrl = (url + "?page=" + str(i))
            driver.get(nextUrl)

            tmp = driver.find_elements_by_css_selector('.RMUi2 a')

            for elem in tmp:
                hrefs.append(elem.get_attribute("href"))

            print(hrefs[tmp2-1:])
            tmp2 += len(tmp)

        return rval, hrefs
    else:
        return -1, []
