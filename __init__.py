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
import datetime

from mycroft_jarbas_utils.browser import BrowserControl

from mycroft.skills.settings import SkillSettings
from adapt.intent import IntentBuilder
from mycroft.util.log import getLogger
from mycroft.dialog import DialogLoader
from mycroft.messagebus.message import Message
from mycroft.api import Api
from mycroft.skills.core import MycroftSkill, intent_handler, intent_file_handler
from mycroft.util.log import LOG
from mycroft.util.parse import extract_datetime
from mycroft.util.format import nice_number
from mycroft.skills.audioservice import AudioService

from fbchat import Client
from fbchat.models import *

import mycroft.audio

__author__ = 'ldevalbray'


import logging
# disable logs from requests and urllib 3, or there is too much spam from facebook
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = getLogger(abspath(__file__).split('/')[-2])

facebookNames = ["facebook", "face book"]
twitterNames = ['twitter', "twitt er"]
bothNames =['', 'both', 'facebook and twitter', "all", "all my social networks"]
FACEBOOK = "facebook"
TWITTER = "twitter"
BOTH = "both"

class SocialMediaSkill(MycroftSkill):

    def __init__(self):
        super(SocialMediaSkill, self).__init__(name="SocialMediaSkill")
        
    def initialize(self):

        self.load_data_files(dirname(__file__))

        emitter = self.emitter
        self.driver = BrowserControl(emitter)

        if "twUserAccessToken" not in self.settings:
            self.settings["twUserAccessToken"] = None
        if "twUserAccessTokenSecret" not in self.settings:
            self.settings["twUserAccessTokenSecret"] = None 
        
        if "fbUserAccessToken" not in self.settings:
            self.settings["fbUserAccessToken"] = None
        if "fbUserAccessTokenExpirationDate" not in self.settings:
            self.settings["fbUserAccessTokenExpirationDate"] = None 

        self.tw = Twitter(self.settings, self.driver, self.log)
        self.fb = Facebook(self.settings, self.driver, self.log)

        post_intent = IntentBuilder("PostIntent"). \
            require('Post').require('SocialNetwork').build()
        self.register_intent(post_intent,
                             self.handle_post_intent)

        thank_you_intent = IntentBuilder("ThankYouIntent").\
            require("ThankYouKeyword").build()
        self.register_intent(thank_you_intent, self.handle_thank_you_intent)

        how_are_you_intent = IntentBuilder("HowAreYouIntent").\
            require("HowAreYouKeyword").build()
        self.register_intent(how_are_you_intent,
                             self.handle_how_are_you_intent)

        whats_up_intent = IntentBuilder("WhatsUpIntent").\
            require("WhatsupKeyword").build()
        self.register_intent(whats_up_intent,
                             self.handle_whats_up_intent)

    def handle_thank_you_intent(self, message):
        self.speak_dialog("welcome")

    def handle_how_are_you_intent(self, message):
        self.speak_dialog("how.are.you")

    def handle_whats_up_intent(self, message):
        self.speak_dialog("whats.up")

    def handle_post_intent(self, message):
        post = message.data.get("Post")
        socialSaid = message.data.get("SocialNetwork")

        social = getSocialMedia(socialSaid)

        self.speak("posting " + post + " on " + social)

        posted = False
        
        if social == FACEBOOK:
            posted = self.fb.post(post)
        elif social == TWITTER:
            posted = self.tw.post(post)
        else:
            if(self.fb.post(post) and self.tw.post(post)):
                posted = True

        if posted:
            print "Posted !!"
            self.speak_dialog("post")
        else:
            print "Could not post :("

    def stop(self):
        pass


class Facebook():

    def __init__(self, settings, driver, logger):
        
        self.log = logger   
        self.settings = settings
        self.driver = driver
        self.api = None
        self.fbFriends = None
        self.appAccessToken = '185643198851873|6248814e48fd63d0353866ee3de9264f'
        self.URL = 'https://graph.facebook.com/v2.12/'
        self.auth = Auth(settings, driver, logger)
        self.initApi() 

        print self.getFriendId("Audran de valbret")
        
        # picId = self.getProfilePicId("me")
        # self.likePhoto(picId)
        # print self.getLikes("10215117266189517")
        # self.commentPhoto(picId, "test")
        # self.commentPost( "10215117266189517", "Top !")
        # self.post("test", "me", "Audren de Valbray")

    
    def initApi(self):
        if self.login():
            self.api = facebook.GraphAPI(access_token=self.settings["fbUserAccessToken"])
            self.setUserInfo()
            self.log.info("-- LOGGED IN FB --")
        else:
            self.log.error("-- LOG IN FB FAILED --")

    def login(self):

        expired = False

        if "fbUserAccessTokenExpirationDate" in self.settings:
            expToken = self.settings["fbUserAccessTokenExpirationDate"]
            expDate = datetime.datetime.fromtimestamp(expToken).strftime('%Y-%m-%d %H:%M:%S')
            dateNow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print expDate, dateNow
            if expDate > dateNow:
                expired = True

        if ((self.settings["fbUserAccessToken"] is None) or expired ):
            DATA = {'access_token': self.appAccessToken, 'scope':'public_profile, publish_actions, user_friends, publish_actions, user_posts'}
            loginRequest = requests.post(url = self.URL + 'device/login', data = DATA)
            data = loginRequest.json()

            self.log.info("-- LOGGING IN FB --")

            code = data['code']
            userCode = data['user_code']
            verificationURI = data['verification_uri']
            interval = data['interval']

            DATA2 = {'access_token':self.appAccessToken, 'code':code}

            awaitingUserLoginRequest = requests.post(url = self.URL +'device/login_status', data = DATA2)
            awaitingUserLoginRes = awaitingUserLoginRequest.json()

            self.auth.loginFb(verificationURI, userCode)
        
            while 'access_token' not in awaitingUserLoginRes.keys() :
                #print "-------- AWAITING USER RES STATUS ----/" 
                time.sleep(7)
                awaitingUserLoginRequest = requests.post(url = self.URL +'device/login_status', data = DATA2)
                awaitingUserLoginRes = awaitingUserLoginRequest.json()
                print 'Authentification ... ', verificationURI

            if 'access_token' in awaitingUserLoginRes.keys():
                self.settings["fbUserAccessToken"] = awaitingUserLoginRes['access_token']
                self.settings["fbUserAccessTokenExpirationDate"] = awaitingUserLoginRes['expires_in']
                return self.login()
            
            else:
                return False

        return self.auth.signInFb("https://facebook.com/login")
    
    def post(self, message, to="me", tag="none"):
        if self.login():
            if(to != "me"):
                userId = self.getFriendId(to)
                # driver = self.driver
                # driver.get("https://www.facebook.com/"+userId)
                # element = driver.find_elements_by_class_name("navigationFocus")[1]
                # webdriver.ActionChains(driver).move_to_element(element).click(element).perform()
                # inputElement = element.find_element_by_class_name("_1mj")
                # webdriver.ActionChains(driver).move_to_element(inputElement).click(inputElement).send_keys(message).perform()
                # postBtn = driver.find_element_by_class_name("_2dck").find_element_by_xpath("//button[@data-testid='react-composer-post-button']")
                # webdriver.ActionChains(driver).move_to_element(postBtn).click(postBtn).perform()
                # print "Posted on wall", userId

                get_url(self.driver, "m.facebook.com/"+userId)  # profile page
                self.driver.get_element(data=".// *[ @ id = 'u_0_0']", name="post_box", type="xpath")
                
                self.driver.click_element("post_box")
                self.driver.send_keys_to_element(text=message, name="post_box", special=False)
                time.sleep(5)
                self.driver.get_element(data=".//*[@id='timelineBody']/div[1]/div[1]/form/table/tbody/tr/td[2]/div/input", name="post_button", type="xpath")
                return self.driver.click_element("post_button")

            else:

                if tag != "none":
                    tagId = self.getFriends()[findMatchingString(tag, self.getFriends().keys())]["taggableID"]
                    post = self.api.put_object(parent_object=to, connection_name='feed',
                            message=message, tags=[tagId])
                else:
                    post = self.api.put_object(parent_object=to, connection_name='feed',
                            message=message)
                
                return True
        else:
            return False

    def messageFriend(self, message, to):

        try:
            
            self.messengerClient = Client(self.settings["FacebookEmail"], self.settings["FacebookPassword"])

            friendId = self.getFriendId(friend)
            if friendId:
                formattedMessage = make_unicode(message)
                self.messengerClient.send(Message(text=formattedMessage), thread_id=friendId, thread_type=ThreadType.USER)  
                print("Messaged " + friend + " !" )
                return True
            else:
                return False

            self.messengerClient.logout()
        
        except:
            return False

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
    
    def getFriends(self):
        if self.login():
            if(self.fbFriends is None):
                return getAllData(self.api.get_object("me/taggable_friends"), "toReturn[d[\"name\"]] = {\"picture_url\":d[\"picture\"][\"data\"][\"url\"], \"taggableID\":d[\"id\"]}")
            else:
                return self.fbFriends
        else:
            return None

    def getNumberOfFriends(self):
        if self.login():
            return self.api.get_connections(id='me', connection_name='friends')['summary']['total_count']
        else:
            return None

    def getComments(self, postId, userId='me'):
        if self.login():
            if(userId=='me'):
                userId = self.userInfo["id"]
            return getAllData(self.api.get_connections(id=userId+"_"+postId, connection_name='comments'), "toReturn[d[\"from\"]] = d[\"message\"]") 
        else:
            return None

    def getLikes(self, postId, userId='me'):
        if self.login():
            if(userId=='me'):
                userId = self.userInfo["id"]
            return getAllData(self.api.get_connections(id=userId+"_"+postId, connection_name='likes'), "toReturn[d[\"name\"]] = d[\"id\"]") 
        else:
            return None

    def setUserInfo(self):
        if self.login():
            PARAMS = {'access_token':self.settings["fbUserAccessToken"], 'fields':'name, id'}
            userInfoRequest = requests.get(url = self.URL+'me', params = PARAMS)
            self.userInfo = userInfoRequest.json()
            return True
        else: 
            return False

    def search(self, query, typeToSearchFor="user"):
        if self.login():
            return getAllData(self.api.search(type=typeToSearchFor,q=query), "toReturn[d[\"name\"]] = d[\"id\"]") 
        else:
            return None

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
    
    def getFriendId(self, friend, typeToSearchFor="people"):

        userId=None
        fbFriends = self.getFriends()

        foundFriend = findMatchingString(friend, fbFriends.keys())

        print foundFriend

        self.driver.get_url(self.driver, "https://www.facebook.com/search/"+typeToSearchFor+"/?q="+foundFriend)
        time.sleep(1)
        self.driver.get_element(data="//*[@id=\"BrowseResultsContainer\"]/div/div", name="userInfo", type="xpath")
        data = self.driver.get_attribute(attribute = "data-bt", name = "userInfo")
        userId = re.search("id\":(\d*),", data).group(1)
        
        return userId

class Twitter():
    
    def __init__(self, settings, driver, logger):

        self.log = logger
        self.settings = settings
        self.driver = driver
        self.api = None
        self.consumerKey = 'suWlKq5ptOfGP7U2e6QEYcgT0'
        self.consumerSecret = 'e7mvduA4qn1TtkbiWNX30QBDBLg0XcUUjYflrfI77OjK6bf7XE'
        self.auth = Auth(settings, driver, logger)
        self.initApi()
        if "TwFriends" in self.settings:
            self.twFriends = self.settings["TwFriends"]
        else: 
            self.twFriends = None
        # print self.getFriendStatus("Ingrid de Valbray")
        # print self.retweet("Ingrid de Valbray")
       

    def initApi(self):
        if self.login():
            self.api = twitter.Api(consumer_key=self.consumerKey,
                    consumer_secret=self.consumerSecret,
                    access_token_key=self.settings["twUserAccessToken"],
                    access_token_secret=self.settings["twUserAccessTokenSecret"])
            self.log.info("-- LOGGED IN TW --")
        else:
            self.log.error("-- LOGGED IN TW FAILED --")

    def login(self):

        expired = False

        # if self.api is not None:
        #     try:
        #         # self.getFriends()
        #     except twitter.error.TwitterError:
        #         expired = True

        if ((self.settings["twUserAccessToken"] is None) or expired):

            self.log.info("-- LOGGING IN TW --")

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

            authUrl = "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])

            oauth_verifier = self.auth.loginTw(authUrl)

            token = oauth.Token(request_token['oauth_token'],
                request_token['oauth_token_secret'])
            token.set_verifier(oauth_verifier)
            client = oauth.Client(consumer, token)

            resp, content = client.request(access_token_url, "POST")
            access_token = dict(urlparse.parse_qsl(content))

            if access_token is not None:
                self.settings["twUserAccessToken"] = access_token['oauth_token']
                self.settings["twUserAccessTokenSecret"] = access_token['oauth_token_secret']
                return self.login()
            else:
                return False

        return self.auth.signInTw("https://twitter.com/login")

    def post(self, message, to="me"):
        if self.login():
            if(to=="me"):
                self.api.PostUpdate(message)
            
            else:
                friendFound = findMatchingString(to, self.getFriends().keys())
                self.api.PostUpdate("@"+self.getFriends()[friendFound]["username"]+" "+message)
            return True
        else:
            return False
        
    def getFriendStatus(self, friend):
        if self.login():
            friendFound = findMatchingString(friend, self.getFriends().keys())
            return self.getFriends()[friendFound]["status"]["text"]
        else:
            return None

    def retweet(self, friend):
        if self.login():
            friendFound = findMatchingString(friend, self.getFriends().keys())
            self.api.PostRetweet(self.getFriends()[friendFound]["status"]["id"])
            return True
        return False

    def message(self, message, friend):
        if self.login():
            friendFound = findMatchingString(friend, self.getFriends().keys())
            friendObject=self.getFriends()[friendFound]
            self.api.PostDirectMessage(message, user_id=friendObject["status"]["id"], screen_name=friendObject["username"])
            return True
        else:
            return False

    def getFriends(self):
        if self.login():
            if(self.twFriends is None):
                toReturn = {}
                users = self.api.GetFriends()
                for u in users:
                    toReturn[u.name]={"username":u.screen_name, "id":u.id, "status":{"text":u.status.text, "id":u.status.id}}
                
                self.settings["twFriends"] = toReturn
                return toReturn
            else:
                return self.twFriends
        else:
            return None

# This class manages all the authentication part of the social networs (Signing in, Logging in (to the SDKs) and checks if the user is signed in)
class Auth:

    # We take the logger, driver and settings from the upper classes
    def __init__(self, settings, driver, logger):
        self.log = logger
        self.settings = settings
        self.driver = driver

    # Checks if the user is logged in to FB
    def isLoggedInFb(self, openUrl=True):
        #Open the login page of facebook
        if openUrl is True:
            self.driver.open_url("https://facebook.com/login")
            time.sleep(2)

        title = self.driver.get_title()
        #if there is no title on the opened page, returns false
        if title is None:
            self.log.error("User not logged in in Facebook")
            return False
        #if there is the string Log in in the title, returns false -> user not connected
        elif "Log in" in title or "Log into" in title or "Login" in title or "Verify" in title:
            self.log.error("User not logged in in Facebook")
            return False
        #Else returns true -> user connected
        else:
            self.log.info("User logged in in Facebook")
            return True

    # Checks if the user is logged in to TW
    def isLoggedInTw(self, openUrl=True):
        #Open the login page of TW
        if openUrl is True:
            self.driver.open_url("https://twitter.com/login")
            time.sleep(2)

        title = self.driver.get_title()
        #if there is no title on the opened page, returns false
        if title is None:
            self.log.error("User not logged in in Twitter")
            return False
        #if there is the string Login in the title, returns false -> user not connected
        elif "Log in" in title or "Log into" in title or "Login" in title or "Verify" in title:
            self.log.error("User not logged in in Twitter")
            return False
        #Else returns true -> user connected
        else:
            self.log.info("User Logged in in Twitter")
            return True
        
    #Logs the user to facebook with selenium
    def signInFb(self, url):
        #Checks if the user is not already logged in
        isLoggedIn = self.isLoggedInFb()
        #If not logged in, log him in
        if not isLoggedIn:
            self.driver.open_url(url)
            time.sleep(2)
            self.driver.get_element(data="email", name="email", type="name")
            self.driver.get_element(data="pass", name="pass", type="name")
            self.driver.send_keys_to_element(text=self.settings["FacebookEmail"], name="email", special=False)
            self.driver.send_keys_to_element(text=self.settings["FacebookPassword"], name="pass", special=False)
            self.driver.send_keys_to_element(text="RETURN", name="pass", special=True)
            time.sleep(5)
            return self.isLoggedInFb(False)
        return isLoggedIn
           
    #Logs the user to twitter with selenium
    def signInTw(self, url):
        #Checks if the user is not already logged in
        isLoggedIn = self.isLoggedInTw()
        #If not logged in, log him in
        if not isLoggedIn:
            self.driver.open_url(url)
            time.sleep(2)
            self.driver.get_element(data="//*[@id=\"page-container\"]/div/div[1]/form/fieldset/div[1]/input", name="emailInput", type="xpath")
            self.driver.get_element(data="//*[@id=\"page-container\"]/div/div[1]/form/fieldset/div[2]/input", name="pwInput", type="xpath")
            self.driver.send_keys_to_element(text=self.settings["TwitterEmail"], name="emailInput", special=False)
            self.driver.send_keys_to_element(text=self.settings["TwitterPassword"], name="pwInput", special=False)
            self.driver.send_keys_to_element(text="RETURN", name="pwInput", special=True)
            time.sleep(2)
            title = self.driver.get_title()
            if "Verify" in title:
                self.driver.get_element(data="challenge_response", name="phoneInput", type="name")
                self.driver.send_keys_to_element(text=self.settings["TwitterPhoneNumber"], name="phoneInput", special=False)
                self.driver.send_keys_to_element(text="RETURN", name="phoneInput", special=True)
            time.sleep(2)
            return self.isLoggedInTw(False)
        return isLoggedIn
      
    #Method to activate the social-network mycroft skill app on his facebook account automatically
    #Works with selenium
    def loginFb(self, url, userCode):
        #Logs in the user and checks if correctly done
        if self.signInFb(url):

            self.driver.open_url(url)
            time.sleep(2)
            #Enters the userCode and accepts all the user confirmations needed
            self.driver.get_element(data="user_code", name="userCodeElement", type="name")
            self.driver.send_keys_to_element(text=userCode, name="userCodeElement", special=False)
            self.driver.send_keys_to_element(text="RETURN", name="userCodeElement", special=True)

            print "--- First Confirmation"
            self.driver.get_element(data="__CONFIRM__", name="firstConfirmation", type="name")
            self.driver.click_element("firstConfirmation")
            print "--- Second Confirmation"
            self.driver.get_element(data="__CONFIRM__", name="secondConfirmation", type="name")
            self.driver.click_element("secondConfirmation")


    #Method to activate the social-network mycroft skill app on his twitter account automatically
    #Works with selenium
    def loginTw(self, url):
        userCode = ""
        #Logs in the user and checks if correctly done
        if self.signInTw(url):
            self.driver.open_url(url)
            time.sleep(1)
            #Accepts all the user confirmations needed and gets the userCode
            self.driver.get_element(data="challenge_response", name="phoneInput", type="name")
            self.driver.send_keys_to_element(text=self.settings["TwitterPhoneNumber"], name="phoneInput", special=False)
            self.driver.send_keys_to_element(text="RETURN", name="phoneInput", special=True)
            self.driver.get_element(data="allow", name="allow", type="id")
            self.driver.click_element("allow")

            self.driver.get_element(data="//kbd[@aria-labelledby='code-desc']", name="userCode", type="xpath")
            userCode = self.driver.get_element_text(name="userCode")
        
        #returns the userCode to keep goind on the authentication process
        return userCode

#Returns the Levenstein distance between two strings
def dist(name1, name2):
    if isinstance(name1, str):
        name1 = unicode(name1, "utf-8")
    if isinstance(name2, str):
        name2 = unicode(name2, "utf-8")
    return ratio(name1, name2)

def getSocialMedia(socialMedia):
    toReturn = BOTH
    distance = 0
    for name in facebookNames:
        tmpDist = dist(name, socialMedia)
        if tmpDist > distance:
            toReturn = FACEBOOK
            distance = tmpDist
    for name1 in twitterNames:
        tmpDist = dist(name1, socialMedia)
        if tmpDist > distance:
            toReturn = TWITTER
            distance = tmpDist
    for name2 in bothNames:
        tmpDist = dist(name2, socialMedia)
        if tmpDist > distance:
            toReturn = BOTH
            distance = tmpDist
    return toReturn

def get_url(driver, urlToFetch):
    url = driver.get_current_url()
    url2 = url
    driver.open_url(urlToFetch)
    while url2 == url:
        url2 = driver.get_current_url()
        time.sleep(0.1)

def findMatchingString(name, listOfNames):
    closest = 0
    closestName = None
    for s in listOfNames:
        distance = dist(name, s)
        if( distance > closest):
            closest = distance
            closestName = s

    return closestName

def is_number(n):
    try:
        float(n)
    except ValueError:
        return False
    return True

def getAllData(data, code):
    toReturn = {}
    print "data", data
    for d in data["data"]:
        exec(code)
    while("next" in data["paging"]):
        data = requests.get(data["paging"]["next"]).json()
        for d in data["data"]:
            exec(code)
    
    return toReturn


def create_skill():
    return SocialMediaSkill()