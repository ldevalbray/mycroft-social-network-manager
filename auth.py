import sys
from os.path import dirname
sys.path.append(dirname(dirname(__file__)))

import os  
import time
from browser_service import BrowserControl
from utils import check_exists_by_name, check_exists_by_id, check_exists_by_xpath

class Auth:

    def __init__(self):
        self.chrome_options = Options()  
        self.chrome_options.add_argument("--disable-notifications")
        # chrome_options.add_argument("--headless")  

        self.fbDriver = None
        self.twDriver = None

        # self.driver = webdriver.PhantomJS()
        # self.driver.save_screenshot('screen.png')

        self.fbCredentials = {"email": "l.devalbray@gmail.com", "pw":"azerty050197ytreza"} 
        # self.fbCredentials = {"email": "wworqpucgw_1516816755@tfbnw.net", "pw":"mdptest"} 
        self.twCredentials = {"email": "l.devalbray@gmail.com", "pw":"Briott49", "phoneNumber":"+33613396586"}
        
    def signInFb(self, url):
        if(self.fbDriver is None):
            # self.fbDriver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"),   chrome_options=self.chrome_options) 
            self.fbDriver = BrowserControl(self.emitter)
        self.fbDriver.implicitly_wait(2)
        self.fbDriver.open_url(url)
        if(check_exists_by_name("login", self.fbDriver)):
            self.fbDriver.get_element(data="email", name="email", type="name")
            self.fbDriver.send_keys_to_element(text=self.fbCredentials["email"], name="email", special=False)
            self.fbDriver.get_element(data="pass", name="pass", type="name")
            self.fbDriver.send_keys_to_element(text=self.fbCredentials["pw"], name="pass", special=False)
            self.fbDriver.get_element(data="login", name="login", type="name")
            self.fbDriver.click_element("login")
           

    # def signInTw(self, url):
    #     if(self.twDriver is None):
    #         # self.twDriver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"),   chrome_options=self.chrome_options) 
    #         self.twDriver = BrowserControl(self.emitter)
    #     self.twDriver.implicitly_wait(2)
    #     self.twDriver.open_url(url)
    #     if(check_exists_by_name("session[password]", self.twDriver)):
    #         emailInput = self.twDriver.find_element_by_name("session[username_or_email]")
    #         pwInput = self.twDriver.find_element_by_name("session[password]")
    #         emailInput.send_keys(self.twCredentials["email"])
    #         pwInput.send_keys(self.twCredentials["pw"])
    #         pwInput.send_keys(Keys.RETURN)

    # def loginFb(self, url, userCode):
    #     self.signInFb(url)

    #     userCodeElement = self.fbDriver.find_element_by_name("user_code")
    #     userCodeElement.send_keys(userCode)
    #     userCodeElement.send_keys(Keys.RETURN)

    #     if(check_exists_by_name("__CONFIRM__", self.fbDriver)):
    #         print "--- First Confirmation"
    #         self.fbDriver.find_element_by_name("__CONFIRM__").click()
    #         if(check_exists_by_name("__CONFIRM__", self.fbDriver)):
    #             print "--- Second Confirmation"
    #             self.fbDriver.find_element_by_name("__CONFIRM__").click()


    #     # self.driver.close()

    # def loginTw(self, url):
    #     self.signInTw(url)

    #     userCode = ""

    #     if(check_exists_by_name("challenge_response", self.twDriver)):
    #         phoneInput = self.twDriver.find_element_by_name("challenge_response")
    #         phoneInput.send_keys(self.twCredentials["phoneNumber"])
    #         phoneInput.send_keys(Keys.RETURN)
    #         if(check_exists_by_id("allow", self.twDriver)):
    #             self.find_element_by_id("allow").click()


    #     if(check_exists_by_xpath("//kbd[@aria-labelledby='code-desc']", self.twDriver)):
    #         userCodeElement = self.twDriver.find_element_by_xpath("//kbd[@aria-labelledby='code-desc']")
    #         userCode = userCodeElement.text
        
    #     # self.driver.close()
    #     print userCode
    #     return userCode

    def getFbDriver(self):
        if(self.fbDriver is None):
            self.fbDriver = BrowserControl(self.emitter)
            # self.fbDriver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"),   chrome_options=self.chrome_options) 

        return self.fbDriver

    def getTwDriver(self):
        if(self.twDriver is None):
            self.twDriver = BrowserControl(self.emitter)
            # self.twDriver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"),   chrome_options=self.chrome_options) 
        return self.twDriver


