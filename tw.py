import time
import twitter
import oauth2 as oauth
import urlparse

class Twitter():
    
    def __init__(self):

        self.api = None
        self.consumerKey = 'suWlKq5ptOfGP7U2e6QEYcgT0'
        self.consumerSecret = 'e7mvduA4qn1TtkbiWNX30QBDBLg0XcUUjYflrfI77OjK6bf7XE'
        #self.userAccessToken = None
        self.userAccessToken = '931527061457571840-3u23arFdxoodBOvuxRyJ1QJqA1hXaTY'
        self.userAccessTokenSecret = '5DquBNlWTZVvQ4EYlpoP9GfJEwVq2H77qESKYckGhlkf2'
        self.initApi()
       

    def initApi(self):
        if self.login():
            self.api = twitter.Api(consumer_key=self.consumerKey,
                    consumer_secret=self.consumerSecret,
                    access_token_key=self.userAccessToken,
                    access_token_secret=self.userAccessTokenSecret)

    def login(self):
        print '//// LOGGING IN ////'

        if self.userAccessToken is None:
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

            print "Request Token:"
            print "    - oauth_token        = %s" % request_token['oauth_token']
            print "    - oauth_token_secret = %s" % request_token['oauth_token_secret']
            print 

            print "Go to the following link in your browser:"
            print "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])
            print 

            accepted = 'n'
            while accepted.lower() == 'n':
                accepted = raw_input('Have you authorized me? (y/n) ')
            oauth_verifier = raw_input('What is the PIN? ')

            token = oauth.Token(request_token['oauth_token'],
                request_token['oauth_token_secret'])
            token.set_verifier(oauth_verifier)
            client = oauth.Client(consumer, token)

            resp, content = client.request(access_token_url, "POST")
            access_token = dict(urlparse.parse_qsl(content))

            print "Access Token:"
            print "    - oauth_token        = %s" % access_token['oauth_token']
            print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
            print
            print "You may now access protected resources using the access tokens above." 
            print

            if access_token is not None:
                self.userAccessToken = access_token['oauth_token']
                self.userAccessTokenSecret = access_token['oauth_token_secret']
                return self.login()
            else:
                return False

        else:
            return True

    def post(self, message):
        status = self.api.PostUpdate(message)
        print(status.text)