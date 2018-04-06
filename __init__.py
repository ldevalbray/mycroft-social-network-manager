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
import re

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

        self.tw = Twitter(self.settings, self.driver, self.log, self.getConfirmation, self.speak, emitter)
        self.fb = Facebook(self.settings, self.driver, self.log, self.getConfirmation, self.speak, emitter)

        self.declareIntents()

       

    def declareIntents(self):

        #both twitter and fb intents

        #login
        login_intent = IntentBuilder("LoginIntent"). \
            require('LoginIntentKeyword'). \
            build()
        self.register_intent(login_intent,
                             self.handle_login_intent)

        #logout
        logout_intent = IntentBuilder("LogoutIntent"). \
            require('LogoutIntentKeyword'). \
            build()
        self.register_intent(logout_intent,
                             self.handle_logout_intent) 

        #message test to louis de valbray
        message_intent = IntentBuilder("MessageIntent"). \
            require('MessageIntentKeyword'). \
            require('Message'). \
            require('Person'). \
            build()
        self.register_intent(message_intent, 
                             self.handle_message_intent)

        #post test to louis 
        share_intent = IntentBuilder("ShareIntent"). \
            require('ShareIntentKeyword'). \
            require('Share'). \
            require('Person'). \
            build()
        self.register_intent(share_intent,
                             self.handle_share_intent)

        #post test
        post_intent = IntentBuilder("PostIntent"). \
            require('PostIntentKeyword'). \
            require('Post'). \
            build()
        self.register_intent(post_intent,
                             self.handle_post_intent)

        #facebook only intents

        #comment test on louis de valbray profile picture
        comment_intent = IntentBuilder("CommentIntent"). \
            require('CommentIntentKeyword'). \
            require('Comment'). \
            require('Person'). \
            build()
        self.register_intent(comment_intent,
                             self.handle_comment_intent)

        #like the profile picture of louis de valbray
        like_intent = IntentBuilder("LikeIntent"). \
            require('LikeIntentKeyword'). \
            require('Person'). \
            build()
        self.register_intent(like_intent,
                             self.handle_like_intent)

        #how many friends do i have ?
        friends_number_intent = IntentBuilder("FriendsNumberIntent"). \
            require('NumberOfFriendsIntentKeyword'). \
            build()
        self.register_intent(friends_number_intent,
                             self.handle_friends_number_intent)

         #twitter only intents

        #retweet louis
        retweet_intent = IntentBuilder("RetweetIntent"). \
            require('RetweetIntentKeyword'). \
            require('Retweet'). \
            build()
        self.register_intent(retweet_intent,
                             self.handle_retweet_intent)

        #get/fetch louis status
        friend_status_intent = IntentBuilder("FriendsStatusIntent"). \
            require('StatusIntentKeyword'). \
            require('TwitterStatus'). \
            build()
        self.register_intent(friend_status_intent,
                             self.handle_friend_status_intent)



    def handle_login_intent(self, message):

        socialSaid = self.getSocialNetworkConfirmation()

        social = getSocialMedia(socialSaid)

        login = False
        
        if social == FACEBOOK:
            login = self.fb.login()
        elif social == TWITTER:
            login = self.tw.login()
        else:
            if(self.fb.login() and self.tw.login()):
                login = True

        if login:
            if social == FACEBOOK:
                self.speak_dialog("loggedInFb")
            elif social == TWITTER:
                self.speak_dialog("loggedInTw")
            else:
                self.speak_dialog("loggedInFb")
                self.speak_dialog("loggedInTw")

            self.speak("Logged in successfully")
        else:
            self.speak("Failed to log in")

    def handle_logout_intent(self, message):
        socialSaid = self.getSocialNetworkConfirmation()
        social = getSocialMedia(socialSaid)
        logout = False
        
        if social == FACEBOOK:
            logout = self.fb.logout()
        elif social == TWITTER:
            logout = self.tw.logout()
        else:
            if(self.fb.logout() and self.tw.logout()):
                logout = True

        if logout:
            if social == FACEBOOK:
                self.speak_dialog("loggedOutFb")
            elif social == TWITTER:
                self.speak_dialog("loggedOutTw")
            else:
                self.speak_dialog("loggedOutFb")
                self.speak_dialog("loggedOutTw")

            self.speak("Logged out successfully")
        else:
            self.speak("Failed to log out")

    def handle_post_intent(self, message):
        post = message.data.get("Post")
        socialSaid = self.getSocialNetworkConfirmation()
        social = getSocialMedia(socialSaid)
        
        if self.getConfirmation("post.confirmation", dict(text=post, socialNetwork=social)):
            
            if social == FACEBOOK:
                if self.fb.post(post):
                    self.speak_dialog("post", dict(socialNetwork="Facebook"))
                else:
                    self.speak("Sorry, I could not post your message on Facebook")

            elif social == TWITTER:
                if self.tw.post(post) :
                    self.speak_dialog("post", dict(socialNetwork="Twitter"))
                else:
                    self.speak("Sorry, I could not post your message on Twitter")
                    
            else:
                if self.fb.post(post):
                    self.speak_dialog("post", dict(socialNetwork="Facebook"))
                else:
                    self.speak("Sorry, I could not post your message on Facebook")

                if self.tw.post(post) :
                    self.speak_dialog("post", dict(socialNetwork="Twitter"))
                else:
                    self.speak("Sorry, I could not post your message on Twitter")

    
    def handle_share_intent(self, message):
        post = message.data.get("Share")
        person = message.data.get("Person")
        socialSaid = self.getSocialNetworkConfirmation()

        social = getSocialMedia(socialSaid)


        if self.getConfirmation("postTo.confirmation", dict(text=post, person=person, socialNetwork=social)):

            if social == FACEBOOK:
                if self.fb.post(post, person):
                    self.speak_dialog("post", dict(socialNetwork="Facebook"))
                else:
                    self.speak("Sorry, I could not post your message on Facebook")

            elif social == TWITTER:
                if self.tw.post(post, person) :
                    self.speak_dialog("post", dict(socialNetwork="Twitter"))
                else:
                    self.speak("Sorry, I could not post your message on Twitter")
                    
            else:
                if self.fb.post(post, person):
                    self.speak_dialog("post", dict(socialNetwork="Facebook"))
                else:
                    self.speak("Sorry, I could not post your message on Facebook")

                if self.tw.post(post, person) :
                    self.speak_dialog("post", dict(socialNetwork="Twitter"))
                else:
                    self.speak("Sorry, I could not post your message on Twitter")

         

    def handle_message_intent(self, message):
        messageText = message.data.get("Message")
        person = message.data.get("Person")
        socialSaid = self.getSocialNetworkConfirmation()

        social = getSocialMedia(socialSaid)

        if self.getConfirmation("message.confirmation", dict(text=messageText, person=person, socialNetwork=social)):
            
            if social == FACEBOOK:
                if self.fb.message(messageText, person):
                    self.speak_dialog("Message", dict(socialNetwork="facebook"))
                else:
                    self.speak("Sorry, I could not send your message on facebook")

            elif social == TWITTER:
                if self.tw.message(messageText, person):
                    self.speak_dialog("Message", dict(socialNetwork="twitter"))
                else:
                    self.speak("Sorry, I could not send your message on twitter")
            else:
                if self.fb.message(messageText, person):
                    self.speak_dialog("Message", dict(socialNetwork="facebook"))
                else:
                    self.speak("Sorry, I could not send your message on facebook")
                
                if self.tw.message(messageText, person):
                    self.speak_dialog("Message", dict(socialNetwork="twitter"))
                else:
                    self.speak("Sorry, I could not send your message on twitter")

    #Specific to facebook

    def handle_comment_intent(self, message):
        person = message.data.get("Person")
        comment = message.data.get("Comment")

        if self.fb.commentProfilePic(comment, person):
            self.speak("Comment posted successfully !")
        else:
            self.speak("Sorry, I could not comment" )

    def handle_like_intent(self, message):
        person = message.data.get("Person")

        if self.fb.likeProfilePic(person):
            self.speak("Liked the profile picture succesfully !")
        else:
            self.speak("Sorry, I could not like the profile picture" )

    def handle_friends_number_intent(self, message):
        numberofFriends = self.fb.getNumberOfFriends()
        if numberofFriends:
            self.speak("You have " + str(numberofFriends) + " friends on facebook")
        else:
            self.speak("I could not retrieve the number of friends you have on facebook")

    #Specific to twitter

    def handle_retweet_intent(self, message):
        person = message.data.get("Retweet")

        if self.tw.retweet(person):
            self.speak("Retweeted")
        else:
            self.speak("Failed to retweet")
    
    def handle_friend_status_intent(self, message):
        person = message.data.get("TwitterStatus")

        status = self.tw.getFriendStatus(person)

        if status:
            self.speak(status)
        else:
            self.speak("Failed to get the status")

    def getConfirmation(self, dialog, data):
        try:
            response = self.get_response(dialog,data)
            if response and response == "yes":
                return True
            else:
                self.speak_dialog('noAction')
                return False
        except:
            return False

    def getSocialNetworkConfirmation(self):
        try:
            response = self.get_response("socialNetwork.confirmation")
            return getSocialMedia(response)
        except:
            return getSocialMedia("both")

    def stop(self):
        pass


class Facebook():

    def __init__(self, settings, driver, logger, getConfirmation, speak, emitter):
        
        self.log = logger   
        self.settings = settings
        self.driver = driver
        self.api = None
        self.fbFriends = None
        self.getConfirmation = getConfirmation
        self.speak = speak
        self.emitter = emitter

        self.messengerClient = None
       
        self.URL = 'https://graph.facebook.com/v2.12/'
        self.auth = Auth(settings, driver, logger)
        self.initApi() 

    
    def initApi(self):

        if "fbAppAccessToken" not in self.settings:
            self.appAccessToken = '185643198851873|6248814e48fd63d0353866ee3de9264f'
        elif not self.settings["fbAppAccessToken"]:
            self.appAccessToken = '185643198851873|6248814e48fd63d0353866ee3de9264f'
        else:
            self.appAccessToken = self.settings["fbAppAccessToken"]

        if self.login():
            self.api = facebook.GraphAPI(access_token=self.settings["fbUserAccessToken"])
            self.setUserInfo()
            self.speak("logged in facebook successfully")
            self.log.info("-- LOGGED IN FB --")
        else:
            self.speak("logging in facebook failed")
            self.log.error("-- LOG IN FB FAILED --")


    def login(self):

        expired = False

        if not self.messengerClient:
            self.messengerClient = Client(self.settings["FacebookEmail"], self.settings["FacebookPassword"])

        if "fbUserAccessTokenExpirationDate" in self.settings:
            expToken = self.settings["fbUserAccessTokenExpirationDate"]
            expDate = datetime.datetime.fromtimestamp(float(expToken)).strftime('%Y-%m-%d %H:%M:%S')
            dateNow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if expDate < dateNow:
                expired = True

        if ((self.settings["fbUserAccessToken"] is None) or expired ):
            DATA = {'access_token': self.appAccessToken, 'scope':'public_profile, publish_actions, user_friends, publish_actions, user_posts'}
            loginRequest = requests.post(url = self.URL + 'device/login', data = DATA)
            data = loginRequest.json()

            self.log.info("-- LOGGING IN FB --")
            self.speak("logging in facebook")

            code = data['code']
            userCode = data['user_code']
            verificationURI = data['verification_uri']
            interval = data['interval']

            DATA2 = {'access_token':self.appAccessToken, 'code':code}

            awaitingUserLoginRequest = requests.post(url = self.URL +'device/login_status', data = DATA2)
            awaitingUserLoginRes = awaitingUserLoginRequest.json()

            self.auth.loginFb(verificationURI, userCode)
        
            while 'access_token' not in awaitingUserLoginRes.keys() :
                time.sleep(7)
                awaitingUserLoginRequest = requests.post(url = self.URL +'device/login_status', data = DATA2)
                awaitingUserLoginRes = awaitingUserLoginRequest.json()

            if 'access_token' in awaitingUserLoginRes.keys():
                self.settings["fbUserAccessToken"] = awaitingUserLoginRes['access_token']
                expirationDate = datetime.datetime.now() + datetime.timedelta(0,awaitingUserLoginRes['expires_in'])
                self.settings["fbUserAccessTokenExpirationDate"] = expirationDate.strftime('%s')
                
                return self.login()
            
            else:
                return False

        return self.auth.signInFb("https://facebook.com/login")

    def logout(self):
        self.settings["fbUserAccessToken"] = None
        driverRestarted = restartDriver(self.driver)
        self.messengerClient.logout()
        self.messengerClient = None

        # return not self.auth.isLoggedInFb() and driverRestarted
        return True

    def post(self, message, to="me", tag="none"):
        if self.login():
            if(to != "me"):
                userId = self.getFriendId(to)

                if userId:
    
                    get_url(self.driver, "m.facebook.com/"+userId)
                    self.driver.get_element(data=".// *[ @ id = 'u_0_0']", name="post_box", type="xpath")
                    
                    self.driver.click_element("post_box")
                    self.driver.send_keys_to_element(text=message, name="post_box", special=False)
                    time.sleep(5)
                    self.driver.get_element(data=".//*[@id='timelineBody']/div[1]/div[1]/form/table/tbody/tr/td[2]/div/input", name="post_button", type="xpath")
                    return self.driver.click_element("post_button")

                else:
                    return False

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

    def message(self, message, friend):

        try:

            if self.login():
      
                friendId = self.getFriendId(friend)
                if friendId:
                    formattedMessage = make_unicode(message)
                    self.messengerClient.send(Message(text=formattedMessage), thread_id=friendId, thread_type=ThreadType.USER)  
                    return True
                else:
                    return False

            else:
                return False
           
        except Exception as e: 
            return False

    def likeProfilePic(self, friend):
        try:
            if self.login():
                friendId = self.getFriendId(friend)
                if friendId:
                    picId = self.getProfilePicId(friendId)
                    # picId = "10214802871649850"
                    return self.likePhoto(picId, False)
                else:
                    return False
            else:
                return False
        except Exception as e: 
            return False

    def commentProfilePic(self, comment, friend):
        try:
            if self.login():
                friendId = self.getFriendId(friend)
                if friendId:
                    picId = self.getProfilePicId(friendId)
                    return self.commentPhoto(comment, picId, False)
                else:
                    return False
            else:
                return False
        except Exception as e: 
            return False

    def likePhoto(self, photoId, checkLogin = True):
        loggedIn = True
        if checkLogin == True:
            loggedIn = self.login()
        
        if loggedIn:
            get_url(self.driver, "https://m.facebook.com/photo.php?fbid="+photoId)

            self.driver.get_element(data="/html/body/div/div/div[2]/div/div[1]/div/div/div[2]/div/table/tbody/tr/td[1]/a", name="like_btn", type="xpath")
            
            liked = False

            if not liked:
                return self.driver.click_element("like_btn")
            else:
                return True
        else:
            return False
    
    def commentPhoto(self, comment, photoId, checkLogin = True):
        loggedIn = True
        if checkLogin == True:
            loggedIn = self.login()
        
        if loggedIn:
            get_url(self.driver, "https://m.facebook.com/photo.php?fbid="+photoId)
            
            self.driver.get_element(data="//*[@id=\"composerInput\"]", name="comment_input", type="xpath")
            self.driver.send_keys_to_element(text=comment, name="comment_input", special=False)
            self.driver.get_element(data="/html/body/div/div/div[2]/div/div[1]/div/div/div[3]/div[2]/div/div/div[5]/form/table/tbody/tr/td[2]/div/input", name="comment_submit", type="xpath")
            return  self.driver.click_element(name="comment_submit")
           
        else:
            return False
    
    def getFriends(self, checkLogin = True):

        loggedIn = True
        if checkLogin == True:
            loggedIn = self.login()
        
        if loggedIn:
            if(self.fbFriends is None):
                try:
            
                    friendsList = {}

                    friends = self.messengerClient.fetchAllUsers()
                    
                    for friend in friends:
                        friendsList[friend.name] = friend.uid

                    self.fbFriends = friendsList
                
                except Exception as e: 
                    return False
            
            return self.fbFriends
        else:
            return None

    def getNumberOfFriends(self, checkLogin = True):
        loggedIn = True
        if checkLogin == True:
            loggedIn = self.login()

        if loggedIn:
            return self.api.get_connections(id='me', connection_name='friends')['summary']['total_count']
        else:
            return None

    def setUserInfo(self, checkLogin = True):
        loggedIn = True
        if checkLogin == True:
            loggedIn = self.login()
        
        if loggedIn:
            PARAMS = {'access_token':self.settings["fbUserAccessToken"], 'fields':'name, id'}
            userInfoRequest = requests.get(url = self.URL+'me', params = PARAMS)
            self.userInfo = userInfoRequest.json()
            return True
        else: 
            return False

    def getProfilePicId(self, friendId):
        picSrc = None
        if friendId == "me":
            friendId = self.userInfo['id']

        r = requests.get("https://graph.facebook.com/"+friendId+"/picture")
        picSrc = r.url
        findString = "\d_(.*)_\d"
        return re.search(findString, picSrc).group(1)
    
    def getFriendId(self, friend, typeToSearchFor="people"):

        userId=None
        fbFriends = self.getFriends()

        foundFriend = findMatchingString(friend, fbFriends.keys())

        if self.getConfirmation("person.confirmation", dict( person=foundFriend )):

            userId = fbFriends[foundFriend]
            
        return userId

    #UNUSED in Mycroft but working methods - can be used in the future
    
    # def getComments(self, postId, userId='me'):
    #     if self.login():
    #         if(userId=='me'):
    #             userId = self.userInfo["id"]
    #         return getAllData(self.api.get_connections(id=userId+"_"+postId, connection_name='comments'), "toReturn[d[\"from\"]] = d[\"message\"]") 
    #     else:
    #         return None

    # def getLikes(self, postId, userId='me'):
    #     if self.login():
    #         if(userId=='me'):
    #             userId = self.userInfo["id"]
    #         return getAllData(self.api.get_connections(id=userId+"_"+postId, connection_name='likes'), "toReturn[d[\"name\"]] = d[\"id\"]") 
    #     else:
    #         return None

    # def search(self, query, typeToSearchFor="user"):
    #     if self.login():
    #         return getAllData(self.api.search(type=typeToSearchFor,q=query), "toReturn[d[\"name\"]] = d[\"id\"]") 
    #     else:
    #         return None

class Twitter():
    
    def __init__(self, settings, driver, logger, getConfirmation, speak, emitter):

        self.log = logger
        self.settings = settings
        self.driver = driver
        self.api = None
        self.getConfirmation = getConfirmation
        self.speak = speak
        self.emitter = emitter

        self.auth = Auth(settings, driver, logger)
        self.initApi()
       
        self.twFriends = None
       

    def initApi(self):

        if "twConsumerKey" not in self.settings:
            self.consumerKey = 'suWlKq5ptOfGP7U2e6QEYcgT0'
        elif not self.settings["twConsumerKey"]:
            self.consumerKey = 'suWlKq5ptOfGP7U2e6QEYcgT0'
        else:
            self.consumerKey = self.settings["twConsumerKey"]

        if "twConsumerSecret" not in self.settings:
            self.consumerSecret = 'e7mvduA4qn1TtkbiWNX30QBDBLg0XcUUjYflrfI77OjK6bf7XE'
        elif not self.settings["twConsumerSecret"]:
            self.consumerSecret = 'e7mvduA4qn1TtkbiWNX30QBDBLg0XcUUjYflrfI77OjK6bf7XE'
        else:
            self.consumerSecret = self.settings["twConsumerSecret"]

        if self.login():
            self.api = twitter.Api(consumer_key=self.consumerKey,
                    consumer_secret=self.consumerSecret,
                    access_token_key=self.settings["twUserAccessToken"],
                    access_token_secret=self.settings["twUserAccessTokenSecret"])
            self.speak("logged in twitter successfully")
            self.log.info("-- LOGGED IN TW --")
        else:
            self.speak("logging in twitter failed")
            self.log.error("-- LOG IN TW FAILED --")

    def login(self):

        expired = False

        # if self.api is not None:
        #     try:
        #         # self.getFriends()
        #     except twitter.error.TwitterError:
        #         expired = True

        if ((self.settings["twUserAccessToken"] is None) or expired):

            self.speak("logging in twitter")
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

            if access_token is not None and 'oauth_token' in access_token:
                self.settings["twUserAccessToken"] = access_token['oauth_token']
                self.settings["twUserAccessTokenSecret"] = access_token['oauth_token_secret']
                return self.login()
            else:
                return False

        return self.auth.signInTw("https://twitter.com/login")

    def logout(self):
        self.settings["twUserAccessToken"] = None
        driverRestarted = restartDriver(self.driver)
        # return not self.auth.isLoggedInTw() and driverRestarted
        return True

    def post(self, message, to="me"):
        if self.login():
            if(to=="me"):
                self.api.PostUpdate(message)
                return True
            
            else:
                friendFound = findMatchingString(to, self.getFriends().keys())
                if self.getConfirmation("person.confirmation", dict( person=friendFound )):
                    self.api.PostUpdate("@"+self.getFriends()[friendFound]["username"]+" "+message)
                    return True
                else:
                    return False
            
        else:
            return False
        
    def getFriendStatus(self, friend):
        if self.login():
            friendFound = findMatchingString(friend, self.getFriends().keys())
            if self.getConfirmation("person.confirmation", dict( person=friendFound )):
                return self.getFriends()[friendFound]["status"]["text"]
            else:
                return None
        else:
            return None

    def retweet(self, friend):
        if self.login():
            friendFound = findMatchingString(friend, self.getFriends().keys())
            if self.getConfirmation("person.confirmation", dict( person=friendFound )):
                self.api.PostRetweet(self.getFriends()[friendFound]["status"]["id"])
                return True
            else:
                return False
        return False

    def message(self, message, friend):
        if self.login():
            friendFound = findMatchingString(friend, self.getFriends().keys())
            if self.getConfirmation("person.confirmation", dict( person=friendFound )):
                friendObject=self.getFriends()[friendFound]
                self.api.PostDirectMessage(message, user_id=friendObject["id"], screen_name=friendObject["username"])
                return True
            else:
                return False
        else:
            return False

    def getFriends(self):
        if self.login():
            if(self.twFriends is None):
                toReturn = {}
                users = self.api.GetFriends()
                for u in users:
                    toReturn[u.name]={"username":u.screen_name, "id":u.id, "status":{"text":u.status.text, "id":u.status.id}}
                
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
            self.driver.open_url("https://m.facebook.com/login")
            
        time.sleep(2)
        title = self.driver.get_title()
        #if there is no title on the opened page, returns false
        if title is None:
            self.log.error("User not logged in in Facebook")
            return False
        #if there is the string Log in in the title, returns false -> user not connected
        elif "Log in" in title or "Log into" in title or "Login" in title or "Verify" in title or "connecter" in title:
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
        elif "Log in" in title or "Log into" in title or "Login" in title or "Verify" in title or "connecter" in title:
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

            time.sleep(1)
            self.driver.get_element(data="__CONFIRM__", name="firstConfirmation", type="name")
            self.driver.click_element("firstConfirmation")
            time.sleep(2)
            self.driver.get_element(data="__CONFIRM__", name="secondConfirmation", type="name")
            self.driver.click_element("secondConfirmation")
            time.sleep(2)
            self.driver.get_element(data="__CONFIRM__", name="thirdConfirmation", type="name")
            self.driver.click_element("thirdConfirmation")
            time.sleep(1)


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
            time.sleep(1)
            self.driver.get_element(data="allow", name="allow", type="id")
            self.driver.click_element("allow")
            time.sleep(1)

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
    if socialMedia is not None:
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

def make_unicode(input):
    if type(input) != unicode:
        input =  input.decode('utf-8')
        return input
    else:
        return input

def getAllData(data, code):
    toReturn = {}
    for d in data["data"]:
        exec(code)
    if "paging" in data:
        while("next" in data["paging"]):
            data = requests.get(data["paging"]["next"]).json()
            for d in data["data"]:
                exec(code)
    
    return toReturn

def restartDriver(driver):
    print "restarting driver"


def create_skill():
    return SocialMediaSkill()