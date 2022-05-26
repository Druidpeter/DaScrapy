import time
import re
import sys

#from selenium import webdriver
#from selenium.webdriver.common.keys import Keys

# TODO: Need to turn the code below into a generator method that
# yields until exhausted, and then returns the string "exhausted"
# continuously until method death.

# The method needs only a gallery url parameter. It then fetches the html
# from all of the associated url gallery pages using selenium when asked.

def HarvestDeviationHTML(url, driver):
    driver.get(url)
    return driver.page_source

# We need to re-implement the original stack functionality, so that we
# only harvest urls underneath divs of class="_1jrTL"

# Instead of returning the html, return hrefs under divs of
# class="_1jrTL" directly.

def HarvestGalleryHTML(url, driver):
    lnStrEx = "(https://www\\.deviantart\\.com/.+/art/.+)\" "
    lnRegEx = re.compile(lnStrEx)
    limitRegEx = re.compile("page=(.+)")

    print("Creating Webdriver using Firefox Backend")

    print("Accessing Driver URL")
    driver.get(url)

    hrefs = driver.find_elements_by_css_selector('._1jrTL a')
    yield [elem.get_attribute("href") for elem in hrefs ]

    print("Calculating additional harvest cycles.")
    elements = driver.find_elements_by_css_selector('._2AnAJ a._14hN5')

    if elements:
        links = [elem.get_attribute('href') for elem in elements]

        index_loc = len(links) - 2
        pageLimit = int(limitRegEx.search(links[index_loc]).group(1))

        print("Harvesting relevant URLs from additional Link cycles")

        for i in range(2, pageLimit): 
            nextUrl = (url + "?page=" + str(i))
            driver.get(nextUrl)

            hrefs = driver.find_elements_by_css_selector('._1jrTL a')
            yield [ elem.get_attribute("href") for elem in hrefs ]

        yield -1
    else:
        yield -1
