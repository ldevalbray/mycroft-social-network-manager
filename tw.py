import sys
from os.path import dirname
sys.path.append(dirname(dirname(__file__)))

import time
import twitter
import oauth2 as oauth
import urlparse
from auth import Auth
from utils import findMatchingString


class Twitter():
    
    def __init__(self, settings):

        self.settings = settings
        self.api = None
        self.consumerKey = 'suWlKq5ptOfGP7U2e6QEYcgT0'
        self.consumerSecret = 'e7mvduA4qn1TtkbiWNX30QBDBLg0XcUUjYflrfI77OjK6bf7XE'
        # self.initApi()
        # self.twFriends = None
        # print self.getFriendStatus("Ingrid de Valbray")
        # print self.retweet("Ingrid de Valbray")
       

    # def initApi(self):
    #     if self.login():
    #         self.api = twitter.Api(consumer_key=self.consumerKey,
    #                 consumer_secret=self.consumerSecret,
    #                 access_token_key=self.settings["twUserAccessToken"],
    #                 access_token_secret=self.settings["twUserAccessTokenSecret"])

    # def login(self, expired = False):
    #     if ((self.settings["twUserAccessToken"] is None) or expired):
    #         print "-------- LOGGING IN TW -------"
    #         consumer_key = self.consumerKey
    #         consumer_secret = self.consumerSecret

    #         request_token_url = 'https://api.twitter.com/oauth/request_token'
    #         access_token_url = 'https://api.twitter.com/oauth/access_token'
    #         authorize_url = 'https://api.twitter.com/oauth/authorize'

    #         consumer = oauth.Consumer(consumer_key, consumer_secret)
    #         client = oauth.Client(consumer)
                
    #         resp, content = client.request(request_token_url, "GET")
    #         if resp['status'] != '200':
    #             raise Exception("Invalid response %s." % resp['status'])

    #         request_token = dict(urlparse.parse_qsl(content))

    #         # print "Request Token:"
    #         # print "    - oauth_token        = %s" % request_token['oauth_token']
    #         # print "    - oauth_token_secret = %s" % request_token['oauth_token_secret']
    #         # print 

    #         authUrl = "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])

    #         oauth_verifier = Auth().loginTw(authUrl)

    #         token = oauth.Token(request_token['oauth_token'],
    #             request_token['oauth_token_secret'])
    #         token.set_verifier(oauth_verifier)
    #         client = oauth.Client(consumer, token)

    #         resp, content = client.request(access_token_url, "POST")
    #         access_token = dict(urlparse.parse_qsl(content))

    #         # print "Access Token:"
    #         # print "    - oauth_token        = %s" % access_token['oauth_token']
    #         # print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
    #         # print
    #         # print "You may now access protected resources using the access tokens above." 
    #         # print

    #         if access_token is not None:
    #             self.settings["twUserAccessToken"] = access_token['oauth_token']
    #             self.settings["twUserAccessTokenSecret"] = access_token['oauth_token_secret']
    #             return self.login()
    #         else:
    #             return False

    #     else:
    #         print ("----- LOGGED IN TW ------")
    #         return True

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
       