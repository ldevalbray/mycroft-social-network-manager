import sys
from os.path import dirname
sys.path.append(dirname(dirname(__file__)))

import requests
import facebook
import time
from auth import Auth
from utils import check_exists_by_name, check_exists_by_id, check_exists_by_xpath, findMatchingString, is_number, getAllData

import re
from browser_service import BrowserControl

class Facebook():

    def __init__(self, settings):

        self.settings = settings
        self.api = None
        self.fbFriends = None
        self.appAccessToken = '185643198851873|6248814e48fd63d0353866ee3de9264f'
        self.URL = 'https://graph.facebook.com/v2.12/'
        self.driver = Auth()
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
        self.driver.signInFb("https://www.facebook.com/login")
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
        
    