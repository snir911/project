from selenium import webdriver

def get_magnet_by_name_pitatebay( name ):
    driver = webdriver.Firefox()
    driver.implicitly_wait(30)
    base_url = "https://thepiratebay.se/"
    
    driver.get(base_url + "/")
    driver.find_element_by_css_selector("input[name=\"q\"]").clear()
    driver.find_element_by_css_selector("input[name=\"q\"]").send_keys(name)
    driver.find_element_by_css_selector("input[type=\"submit\"]").click()
    driver.find_element_by_xpath("//td[2]/div/a").click()
    magnet = driver.find_element_by_css_selector("a[title=\"Get this torrent\"]").get_attribute("href")
    driver.quit()
    return magnet

def get_magnet_Latest_torrent():
    driver = webdriver.Firefox()
    driver.implicitly_wait(30)
    base_url = "https://thepiratebay.se/"
    driver.get(base_url + "/")
    driver.find_element_by_link_text("Recent Torrents").click()
    driver.find_element_by_xpath("//td[2]/div/a").click()
    magnet = driver.find_element_by_css_selector("a[title=\"Get this torrent\"]").get_attribute("href")
    driver.quit()
    return magnet
    
