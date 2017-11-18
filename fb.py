import requests
import facebook
import time

class Facebook():

    def __init__(self):
        self.api = None
        self.appAccessToken = '659166094472687|9f9d0665f86c3a6a88838450bfc50e9b'
        self.URL = 'https://graph.facebook.com/v2.11/'
        #self.userAccessToken = None
        self.userAccessToken = 'EAAJXghDote8BALoPO76iZC926BAzZCllZCzIn1EsWlX6vZBHkUbzzKlZATSl03Olxcrp4QqXmr5QlgKdxi2gxTwcgn7mNHJ6Owz5wrBJqjsI2xWbk8ZBqRfDZBmTracCZC5TBNc0BBQv4sMVnw3hNkV5TIKYgjxOz2cxvynZBTwWVZAAZDZD'
        self.userAccessTokenExpirationDate = '5181085'
        self.initApi()
    
    def initApi(self):
        if self.login():
            self.api = facebook.GraphAPI(access_token=self.userAccessToken)

    def login(self):
        if self.userAccessToken is None:
            DATA = {'access_token': self.appAccessToken, 'scope':'public_profile, publish_actions, user_friends'}
            loginRequest = requests.post(url = self.URL + 'device/login', data = DATA)
            data = loginRequest.json()
            
            print "//////// LOGING IN  /////"
            code = data['code']
            userCode = data['user_code']
            verificationURI = data['verification_uri']
            interval = data['interval']
            print verificationURI
            print userCode

            DATA2 = {'access_token':self.appAccessToken, 'code':code}

            awaitingUserLoginRes = {} 
        
            while 'access_token' not in awaitingUserLoginRes.keys() :
                #print "//////// AWAITING USER RES STATUS /////"
                time.sleep(7)
                awaitingUserLoginRequest = requests.post(url = self.URL +'device/login_status', data = DATA2)
                awaitingUserLoginRes = awaitingUserLoginRequest.json()
                print 'Waiting for user to go to', verificationURI

            if 'access_token' in awaitingUserLoginRes.keys():
                print "//////// LOGGED IN /////"
                self.userAccessToken = awaitingUserLoginRes['access_token']
                self.userAccessTokenExpirationDate = awaitingUserLoginRes['expires_in']
                self.welcomeUser()
                return self.login()
            
            else:
                print "//////// LOG IN FAILED /////"
                return False

        else:
            return True
    
    def welcomeUser(self):
        PARAMS = {'access_token':self.userAccessToken, 'fields':'name'}

        userInfoRequest = requests.get(url = self.URL+'me', params = PARAMS)
        userInfo = userInfoRequest.json()
        print "//////// USER INFO /////"
        print userInfo
        print userInfo['name']
    
    def post(self, message):
        post = self.api.put_object(parent_object='me', connection_name='feed',
                  message=message)
        print post