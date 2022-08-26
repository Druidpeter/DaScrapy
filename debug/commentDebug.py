import sys
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

profile = webdriver.FirefoxProfile()
profile.set_preference("browser.cache.disk.enable", False)
profile.set_preference("browser.cache.memory.enable", False)
profile.set_preference("browser.cache.offline.enable", False)
profile.set_preference("network.http.use-cache", False)
driver = webdriver.Firefox(profile)


driver.get('https://www.deviantart.com/axsens/art/Dragon-ninja-889895934')

# usernames = driver.find_elements_by_css_selector('_2vKEO')

# for username in usernames:
#     print(username.get_attribute('innerHTML'))

button = driver.find_element_by_css_selector('._1lBsK._3_MJY._2vim0._1FKeR')

for i in range(0, 1):
    button.click()
    time.sleep(3)

pagesource = driver.page_source

fd = open("page_source.html", "w")
fd.write(pagesource)
fd.close()
exit()
    
comments = driver.find_elements_by_css_selector('.vJeu0')

for comment in comments:
    print(comment.get_attribute("innerHTML"))

#.vJeu0 > div:nth-child(1)
