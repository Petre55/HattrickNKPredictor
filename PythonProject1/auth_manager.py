"""Authentication and session management
 for Hattrick using Selenium and Requests."""

import os
import time
import requests
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Use script's directory for downloads (cross-platform and relative)
download_dir = os.path.dirname(os.path.abspath(__file__))


class AuthManager:
    """Handles authentication and session transfer for the Hattrick website."""

    def __init__(self, username, password, url):
        self.username = username
        self.password = password
        self.url = url
        self.driver = None

    def setup_browser(self):
        """Sets up headless Firefox browser with download preferences."""
        options = Options()
        options.headless = True
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager"
                               ".showWhenStarting", False)
        options.set_preference("browser.download.dir", download_dir)
        options.set_preference("browser.helperApps.neverAsk."
                               "saveToDisk", "text/csv")
        self.driver = webdriver.Firefox(options=options)

    def accept_cookies(self):
        """Accepts cookies if a pop-up appears."""
        try:
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            '.cky-btn.cky-btn-accept'))
            ).click()
        except TimeoutException:
            pass

    def login(self):
        """Logs in via the main login page."""
        self.setup_browser()
        self.driver.get(self.url)
        self.accept_cookies()
        time.sleep(1)
        self.driver.find_element("link text", "Belépés").click()
        time.sleep(1)
        (self.driver.find_element(By.ID,
                                  "inputLoginname")
         .send_keys(self.username))
        (self.driver.find_element(By.ID,
                                  "inputPassword")
         .send_keys(self.password))
        self.driver.find_element(By.CSS_SELECTOR, "button.primary-button").click()
        time.sleep(1)

    def login_forum(self):
        """Logs in via the forum login page."""
        self.setup_browser()
        self.driver.get(self.url)
        time.sleep(1)
        try:
            self.driver.find_element(By.CSS_SELECTOR,
                                     '.cky-btn.cky-btn-accept').click()
        except TimeoutException:
            pass
        time.sleep(1)
        (self.driver.find_element(By.ID,
                                  "ctl00_ctl00_CPContent_ucLogin_txtUserName")
         .send_keys(self.username))
        (self.driver.find_element(By.ID,
                                  "ctl00_ctl00_CPContent_ucLogin_txtPassword")
         .send_keys(self.password))
        (self.driver.find_element
         (By.ID, 'ctl00_ctl00_CPContent_ucLogin_butLogin').click())
        time.sleep(1)

    def convert_cookies_to_requests(self):
        """Transfers Selenium cookies to a requests session."""
        s = requests.Session()
        for cookie in self.driver.get_cookies():
            s.cookies.set(cookie['name'], cookie['value'])
        return s

    def close(self):
        """Closes the browser if open."""
        if self.driver:
            self.driver.quit()
