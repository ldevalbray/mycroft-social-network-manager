# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.


# Visit https://docs.mycroft.ai/skill.creation for more detailed information
# on the structure of this skill and its containing folder, as well as
# instructions for designing your own skill based on this template.


# Import statements: the list of outside modules you'll be using in your
# skills, whether from other files in mycroft-core or from external libraries

import sys
from os.path import dirname, abspath, basename

sys.path.append(dirname(dirname(__file__)))

import requests
from Levenshtein import ratio
import facebook
import time 
import twitter
import oauth2 as oauth
import urlparse

from mycroft_jarbas_utils.browser import BrowserControl

from mycroft.skills.settings import SkillSettings
from adapt.intent import IntentBuilder
from mycroft.util.log import getLogger
from mycroft.dialog import DialogLoader
from mycroft.messagebus.message import Message
from mycroft.api import Api
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG
from mycroft.util.parse import extract_datetime
from mycroft.util.format import nice_number
from mycroft.skills.audioservice import AudioService

import mycroft.audio

__author__ = 'ldevalbray'

logger = getLogger(abspath(__file__).split('/')[-2])

class SocialMediaSkill(MycroftSkill):

    def __init__(self):
        super(SocialMediaSkill, self).__init__(name="SocialMediaSkill")
        
    def initialize(self):

        self.load_data_files(dirname(__file__))


        emitter = self.emitter
        self.driver = BrowserControl(emitter)

        print(self.settings["FacebookEmail"])

        if "twUserAccessToken" is not in self.settings:
            self.settings["twUserAccessToken"] = None
        if "twUserAccessTokenSecret" is not in self.settings:
            self.settings["twUserAccessTokenSecret"] = None 

        self.FB = 'facebook'
        self.TW = 'twitter'
        # self.fb = Facebook(self.settings, self.driver)
        self.tw = Twitter(self.settings, self.driver)

        LOG.info("TEST 2222222222222222222222", self.settings)

        post_intent = IntentBuilder("PostIntent").\
            require("PostIntentKeyword").build()
        self.register_intent(post_intent,
                             self.handle_post_intent)

        thank_you_intent = IntentBuilder("ThankYouIntent").\
            require("ThankYouKeyword").build()
        self.register_intent(thank_you_intent, self.handle_thank_you_intent)

        how_are_you_intent = IntentBuilder("HowAreYouIntent").\
            require("HowAreYouKeyword").build()
        self.register_intent(how_are_you_intent,
                             self.handle_how_are_you_intent)

        hello_world_intent = IntentBuilder("HelloWorldIntent").\
            require("HelloWorldKeyword").build()
        self.register_intent(hello_world_intent,
                             self.handle_hello_world_intent)

    def handle_thank_you_intent(self, message):
        self.speak_dialog("welcome")

    def handle_how_are_you_intent(self, message):
        self.speak_dialog("how.are.you")

    def handle_hello_world_intent(self, message):
        self.speak_dialog("hello.world")

    def handle_post_intent(self, message):
        print message
        # if social == self.FB:
        #     self.fb.post(message)
        # elif social == self.TW:
        #     self.tw.post(message)
        # else:
        #     self.fb.post(message)
        #     self.tw.post(message)
        self.speak_dialog("post")

    def stop(self):
        pass

class Facebook():

    def __init__(self, settings, driver):

        # self.settings = settings
        self.api = None
        self.fbFriends = None
        self.appAccessToken = '185643198851873|6248814e48fd63d0353866ee3de9264f'
        self.URL = 'https://graph.facebook.com/v2.12/'
        self.settings = settings
        self.auth = Auth(settings, driver)
        self.initApi() 
        # picId = self.getProfilePicId("me")
        # self.likePhoto(picId)
        # print self.getLikes("10215117266189517")
        # self.commentPhoto(picId, "test")
        # self.commentPost( "10215117266189517", "Top !")
        # self.post("test", "me", "Audren de Valbray")

    
    def initApi(self):
        # if self.login():
        #     self.api = facebook.GraphAPI(access_token=self.settings["fbUserAccessToken"])
        #     self.setUserInfo()
        self.login()

    def login(self,expired = False):
        # if ((self.settings["fbUserAccessToken"] is None) or expired ):
        #     DATA = {'access_token': self.appAccessToken, 'scope':'public_profile, publish_actions, user_friends, publish_actions, user_posts'}
        #     loginRequest = requests.post(url = self.URL + 'device/login', data = DATA)
        #     data = loginRequest.json()

        #     print "-------- LOGGING IN FB -------"
        #     code = data['code']
        #     userCode = data['user_code']
        #     verificationURI = data['verification_uri']
        #     interval = data['interval']

        #     DATA2 = {'access_token':self.appAccessToken, 'code':code}

        #     awaitingUserLoginRequest = requests.post(url = self.URL +'device/login_status', data = DATA2)
        #     awaitingUserLoginRes = awaitingUserLoginRequest.json()

        #     self.driver.loginFb(verificationURI, userCode)
        
        #     while 'access_token' not in awaitingUserLoginRes.keys() :
        #         #print "-------- AWAITING USER RES STATUS ----/" 
        #         time.sleep(7)
        #         awaitingUserLoginRequest = requests.post(url = self.URL +'device/login_status', data = DATA2)
        #         awaitingUserLoginRes = awaitingUserLoginRequest.json()
        #         print 'Authentification ... ', verificationURI

        #     if 'access_token' in awaitingUserLoginRes.keys():
        #         self.settings["fbUserAccessToken"] = awaitingUserLoginRes['access_token']
        #         self.settings["fbUserAccessTokenExpirationDate"] = awaitingUserLoginRes['expires_in']
        #         print self.settings
        #         return self.login()
            
        #     else:
        #         print "-------- LOG IN FAILED -------"
        #         return False

        # else:
        self.auth.signInFb("https://www.facebook.com/login")
        print "-------- LOGGED IN FB --------"
        return True
    
    # def post(self, message, to="me", tag="none"):
    #     if(to != "me"):
    #         userId = self.getFriendId(to)
    #         driver = self.driver.getFbDriver()
    #         driver.get("https://www.facebook.com/"+userId)
    #         element = driver.find_elements_by_class_name("navigationFocus")[1]
    #         webdriver.ActionChains(driver).move_to_element(element).click(element).perform()
    #         inputElement = element.find_element_by_class_name("_1mj")
    #         webdriver.ActionChains(driver).move_to_element(inputElement).click(inputElement).send_keys(message).perform()
    #         postBtn = driver.find_element_by_class_name("_2dck").find_element_by_xpath("//button[@data-testid='react-composer-post-button']")
    #         webdriver.ActionChains(driver).move_to_element(postBtn).click(postBtn).perform()
    #         print "Posted on wall", userId

    #     else:
    #         if tag != "none":
    #             tagId = self.getFriends()[findMatchingString(tag, self.getFriends().keys())]["taggableID"]
            
    #         post = self.api.put_object(parent_object=to, connection_name='feed',
    #                 message=message, tags=[tagId])

    # def like(self, url):
    #     driver = self.driver.getFbDriver()
    #     driver.get(url)
    #     likeBtn = driver.execute_script("return document.querySelector('div.rhc.photoUfiContainer').querySelector('span._1mto').querySelector('a')")
    #     if(likeBtn.get_attribute("aria-pressed") == "false"):
    #         driver.execute_script("document.querySelector('div._57w').querySelector('span._1mto').querySelector('a').click()")
    #     else:
    #         print "Already Liked"

    # def likePhoto(self, photoId):
    #    self.like("https://www.facebook.com/photo.php?fbid="+photoId)

    # def likePost(self, postId, userId="me"):
    #     if(userId == "me"):
    #         userId= self.userInfo["id"]
    #     self.like("https://www.facebook.com/"+userId+"/posts/"+postId)
    
    # def comment(self, url, comment):
    #     driver = self.driver.getFbDriver()
    #     driver.get(url)
    #     time.sleep(1)
    #     commentInputsNumber = len(driver.find_elements_by_class_name("UFIAddCommentInput")) - 1
    #     time.sleep(3)
    #     print commentInputsNumber
    #     commentInput = driver.find_elements_by_class_name("UFIAddCommentInput")[commentInputsNumber]
    #     print commentInput
    #     webdriver.ActionChains(driver).move_to_element(commentInput).click().click().perform()
    #     # webdriver.ActionChains(driver).move_to_element(commentInput).click().send_keys(comment).perform()
    #     # .send_keys(comment).send_keys(Keys.RETURN).perform()
    #     # webdriver.ActionChains(driver)

    # def commentPhoto(self, photoId, comment):
    #     self.comment("https://www.facebook.com/photo.php?fbid="+photoId, comment)
    
    # def commentPost(self, postId, comment, userId="me"):
    #     if(userId == "me"):
    #         userId= self.userInfo["id"]
    #     self.comment("https://www.facebook.com/"+userId+"/posts/"+postId, comment)
    
    # def getFriends(self):
    #     if(self.fbFriends is None):
    #         return getAllData(self.api.get_object("me/taggable_friends"), "toReturn[d[\"name\"]] = {\"picture_url\":d[\"picture\"][\"data\"][\"url\"], \"taggableID\":d[\"id\"]}")
    #     else:
    #         return self.fbFriends

    # def getNumberOfFriends(self):
    #     return self.api.get_connections(id='me', connection_name='friends')['summary']['total_count']

    # def getComments(self, postId, userId='me'):
    #     if(userId=='me'):
    #         userId = self.userInfo["id"]
    #     return getAllData(self.api.get_connections(id=userId+"_"+postId, connection_name='comments'), "toReturn[d[\"from\"]] = d[\"message\"]") 

    # def getLikes(self, postId, userId='me'):
    #     if(userId=='me'):
    #         userId = self.userInfo["id"]
    #     return getAllData(self.api.get_connections(id=userId+"_"+postId, connection_name='likes'), "toReturn[d[\"name\"]] = d[\"id\"]") 

    # def setUserInfo(self):
    #     PARAMS = {'access_token':self.settings["fbUserAccessToken"], 'fields':'name, id'}
    #     userInfoRequest = requests.get(url = self.URL+'me', params = PARAMS)
    #     self.userInfo = userInfoRequest.json()

    # def search(self, query, typeToSearchFor="user"):
    #    return getAllData(self.api.search(type=typeToSearchFor,q=query), "toReturn[d[\"name\"]] = d[\"id\"]") 

    # def getProfilePicId(self, friendId):
    #     picSrc = None
    #     if friendId == "me":
    #         friendId = self.userInfo['id']
    #     if is_number(friendId):
    #         r = requests.get("https://graph.facebook.com/"+friendId+"/picture")
    #         picSrc = r.url
    #     else:
    #         friends = self.getFriends()
    #         foundFriend = findMatchingString(friendId, friends.keys())
    #         picSrc = friends[foundFriend]["picture_url"]

    #     findString = "\d_(.*)_\d"
    #     return re.search(findString, picSrc).group(1)
    
    # def getFriendId(self, query, typeToSearchFor="people"):
    #     userId=None
    #     fbFriends = self.getFriends()
    #     foundFriend = findMatchingString(query, fbFriends.keys())
    #     driver = self.driver.getFbDriver()
    #     driver.get("https://www.facebook.com/search/"+typeToSearchFor+"/?q="+foundFriend)
    #     resultsContainer = driver.find_element_by_id("BrowseResultsContainer")
    #     results = resultsContainer.find_elements_by_class_name("_4p2o")
    #     for element in results:
    #         findString = "x\d*\/(.*).jpg"
    #         firstImg = re.search(findString, element.find_element_by_class_name("_1glk").get_attribute("src")).group(1)
    #         scdImg = re.search(findString, fbFriends[foundFriend]).group(1)
    #         if firstImg == scdImg:
    #             data = element.find_element_by_class_name("_3u1").get_attribute("data-bt")
    #             userId = re.search("id\":(\d*),", data).group(1)

    #     return userId

class Twitter():
    
    def __init__(self, settings, driver):

        self.settings = settings
        self.api = None
        self.consumerKey = 'suWlKq5ptOfGP7U2e6QEYcgT0'
        self.consumerSecret = 'e7mvduA4qn1TtkbiWNX30QBDBLg0XcUUjYflrfI77OjK6bf7XE'
        # self.initApi()
        # self.twFriends = None
        # print self.getFriendStatus("Ingrid de Valbray")
        # print self.retweet("Ingrid de Valbray")
       

    def initApi(self):
        if self.login():
            self.api = twitter.Api(consumer_key=self.consumerKey,
                    consumer_secret=self.consumerSecret,
                    access_token_key=self.settings["twUserAccessToken"],
                    access_token_secret=self.settings["twUserAccessTokenSecret"])

    def login(self, expired = False):
        if ((self.settings["twUserAccessToken"] is None) or expired):
            print "-------- LOGGING IN TW -------"
            consumer_key = self.consumerKey
            consumer_secret = self.consumerSecret

            request_token_url = 'https://api.twitter.com/oauth/request_token'
            access_token_url = 'https://api.twitter.com/oauth/access_token'
            authorize_url = 'https://api.twitter.com/oauth/authorize'

            consumer = oauth.Consumer(consumer_key, consumer_secret)
            client = oauth.Client(consumer)
                
            resp, content = client.request(request_token_url, "GET")
            if resp['status'] != '200':
                raise Exception("Invalid response %s." % resp['status'])

            request_token = dict(urlparse.parse_qsl(content))

            # print "Request Token:"
            # print "    - oauth_token        = %s" % request_token['oauth_token']
            # print "    - oauth_token_secret = %s" % request_token['oauth_token_secret']
            # print 

            authUrl = "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])

            oauth_verifier = Auth().loginTw(authUrl)

            token = oauth.Token(request_token['oauth_token'],
                request_token['oauth_token_secret'])
            token.set_verifier(oauth_verifier)
            client = oauth.Client(consumer, token)

            resp, content = client.request(access_token_url, "POST")
            access_token = dict(urlparse.parse_qsl(content))

            # print "Access Token:"
            # print "    - oauth_token        = %s" % access_token['oauth_token']
            # print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
            # print
            # print "You may now access protected resources using the access tokens above." 
            # print

            if access_token is not None:
                self.settings["twUserAccessToken"] = access_token['oauth_token']
                self.settings["twUserAccessTokenSecret"] = access_token['oauth_token_secret']
                return self.login()
            else:
                return False

        else:
            print ("----- LOGGED IN TW ------")
            return True

    # def post(self, message, to="me"):
    #     if(to=="me"):
    #         return self.api.PostUpdate(message)
        
    #     else:
    #         friendFound = findMatchingString(to, self.getFriends().keys())
    #         return self.api.PostUpdate("@"+self.getFriends()[friendFound]["username"]+" "+message)
        
    # def getFriendStatus(self, friend):
    #     friendFound = findMatchingString(friend, self.getFriends().keys())
    #     return self.getFriends()[friendFound]["status"]["text"]

    # def retweet(self, friend):
    #     friendFound = findMatchingString(friend, self.getFriends().keys())
    #     return self.api.PostRetweet(self.getFriends()[friendFound]["status"]["id"])

    # def message(self, message, friend):
    #     friendFound = findMatchingString(friend, self.getFriends().keys())
    #     friendObject=self.getFriends()[friendFound]
    #     return self.api.PostDirectMessage(message, user_id=friendObject["status"]["id"], screen_name=friendObject["username"])


    # def getFriends(self):
    #     if(self.twFriends is None):
    #         toReturn = {}
    #         users = self.api.GetFriends()
    #         for u in users:
    #             toReturn[u.name]={"username":u.screen_name, "id":u.id, "status":{"text":u.status.text, "id":u.status.id}}
    #         return toReturn
    #     else:
    #         return self.twFriends

class Auth:

    def __init__(self, settings, driver):
        # self.chrome_options = Options()  
        # self.chrome_options.add_argument("--disable-notifications")
        # chrome_options.add_argument("--headless")  

        self.settings = settings
        self.driver = driver

        # self.driver = webdriver.PhantomJS()
        # self.driver.save_screenshot('screen.png')

        # self.fbCredentials = {"email": "l.devalbray@gmail.com", "pw":"azerty050197ytreza"} 
        # self.fbCredentials = {"email": "wworqpucgw_1516816755@tfbnw.net", "pw":"mdptest"} 
        # self.twCredentials = {"email": "l.devalbray@gmail.com", "pw":"Briott49", "phoneNumber":"+33613396586"}
        
    def signInFb(self, url):
        self.driver.open_url(url)
        if(check_exists_by_name("login", self.driver)):
            self.driver.get_element(data="email", name="email", type="name")
            self.driver.send_keys_to_element(text=self.settings["FacebookEmail"], name="email", special=False)
            self.driver.get_element(data="pass", name="pass", type="name")
            self.driver.send_keys_to_element(text=self.settings["FacebookPassword"], name="pass", special=False)
            self.driver.get_element(data="login", name="login", type="name")
            self.driver.click_element("login")
           

    def signInTw(self, url):
        # if(self.driver is None):
            # self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"),   chrome_options=self.chrome_options) 
            # self.driver = BrowserControl(self.emitter)
        self.driver.open_url(url)
        if(check_exists_by_name("session[password]", self.driver)):
            self.driver.get_element(data="session[username_or_email]", name="emailInput", type="name")
            self.driver.get_element(data="session[password]", name="pwInput", type="name")
            emailInput = self.driver.find_element_by_name("session[username_or_email]")
            pwInput = self.driver.find_element_by_name("session[password]")
            self.driver.send_keys_to_element(text=self.settings["TwitterEmail"], name="emailInput", special=False)
            self.driver.send_keys_to_element(text=self.settings["TwitterPassword"], name="pwInput", special=False)
            self.driver.send_keys_to_element(text="RETURN", name="pwInput", special=True)

    # def loginFb(self, url, userCode):
    #     self.signInFb(url)

    #     userCodeElement = self.driver.find_element_by_name("user_code")
    #     userCodeElement.send_keys(userCode)
    #     userCodeElement.send_keys(Keys.RETURN)

    #     if(check_exists_by_name("__CONFIRM__", self.driver)):
    #         print "--- First Confirmation"
    #         self.driver.find_element_by_name("__CONFIRM__").click()
    #         if(check_exists_by_name("__CONFIRM__", self.driver)):
    #             print "--- Second Confirmation"
    #             self.driver.find_element_by_name("__CONFIRM__").click()


    #     # self.driver.close()

    def loginTw(self, url):
        self.signInTw(url)

        userCode = ""

        if(check_exists_by_name("challenge_response", self.driver)):
            self.driver.get_element(data="challenge_response", name="phoneInput", type="name")
            self.driver.send_keys_to_element(text=self.settings["TwitterPhoneNumber"], name="phoneInput", special=False)
            self.driver.send_keys_to_element(text="RETURN", name="phoneInput", special=True)
            if(check_exists_by_id("allow", self.driver)):
                self.driver.get_element(data="allow", name="allow", type="id")
                self.driver.click_element("allow")


        if(check_exists_by_xpath("//kbd[@aria-labelledby='code-desc']", self.driver)):
            self.driver.get_element(data="//kbd[@aria-labelledby='code-desc']", name="userCode", type="xpath")
            userCode = self.browser.get_element_text(name="userCode")
        
        # self.driver.close()
        print userCode
        return userCode

def dist(name1, name2):
    if isinstance(name1, str):
        name1 = unicode(name1, "utf-8")
    if isinstance(name2, str):
        name2 = unicode(name2, "utf-8")
    return ratio(name1, name2)

def findMatchingString(name, listOfNames):
    closest = 0
    closestName = None
    for s in listOfNames:
        distance = dist(name, s)
        if( distance > closest):
            closest = distance
            closestName = s

    return closestName

def check_exists_by_xpath(xpath, driver):
    # try:
    #     driver.get_element(data=xpath, name="xpath", type="xpath")
    # except NoSuchElementException:
    #     return False
    return True

def check_exists_by_name(name, driver):
    # try:
    #     driver.get_element(data=name, name="name", type="name")
    # except NoSuchElementException:
    #     return False
    return True

def check_exists_by_id(id, driver):
    # try:
    #     driver.get_element(data=id, name="id", type="id")
    # except NoSuchElementException:
    #     return False
    return True

def is_number(n):
    try:
        float(n)
    except ValueError:
        return False
    return True

def getAllData(data, code):
    toReturn = {}
    for d in data["data"]:
        exec(code)
    while("next" in data["paging"]):
        data = requests.get(data["paging"]["next"]).json()
        for d in data["data"]:
            exec(code)
    
    return toReturn


def create_skill():
    return SocialMediaSkill()