# Mycroft-Social-Network-Manager
Mycroft-Social-Network-Manager is a *skill* developped for [Mycroft][mycroftwebsite]

### Description

> It permits the user to manage his social networks
> (for now, Twitter and Facebook)
> threw Mycroft personal assistant
> WITH YOUR VOICE !

### Usage

Thanks to Mycroft-Social-Network-Manager, you can interact with Mycroft in such ways :

*The following works with both **Twitter and Facebook**, the skill will ask you on which social network you want to perform the action ! (Facebook, Twitter or Facebook and Twitter | both)*

* Login to twitter and facebook
    >Login
* Logout from twitter and facebook
    >Logout
* Send a message to a friend
    >Message [message_text] to [friend_name]
    >Send [message_text] to [friend_name]
    >Text [message_text] to [friend_name]
* Post / tweet something on your wall
    >Post [message_text] 
    >Publish [message_text] 
* Post / tweet something to a friend's wall (tags the friend in your tweet on Tweeter)
    >Share [message_text] to [friend_name]

*The following works with **Facebook** only*

* Comment something on a friend profile picture
    >Comment [message_text] on [friend_name] profile picture
    >Comment [message_text] on [friend_name] pic
    >Comment [message_text] on [friend_name] photo

* Like a friend profile picture
    >Like the profile picture of [friend_name]
    >Like the pic of [friend_name]
    >Like the photo of [friend_name]

* Know your number of friends of Facebook
    >How many friends do I have on Facebook ?

*The following works with **Twitter** only*

* Retweet the last tweet of a friend
    >Retweet [friend_name] 
    >Tweet [friend_name] 

* Reads the last tweet of a friend
    >Get the last tweet of [friend_name]
    >Read the tweeter status of [friend_name]
    >Fetch the last post of [friend_name]


### Installation

Mycroft-Social-Network-Manager requires [Mycroft-core](https://mycroft.ai/get-started/) to run.

In order to install the skill :

```sh
$ cd mycroft-core/msm/
$ ./msm install https://github.com/ldevalbray/mycroft-social-network-manager
```

Installing Mycroft-Social-Network-Manager skill should automatically install [browser_service](https://github.com/JarbasAl/browser_service), another skill that you'll need to run Mycroft-Social-Network-Manager. 

However, browser_service should be made into a priority skill in the mycroft config file :

```sh
    // General skill values
      "skills": {
        ...
        // priority skills to be loaded first
        "priority_skills": ["skill-pairing", "browser_service"],
        ...
      },
```

### Tech

Mycroft-Social-Network-Manager uses a number of open source projects and languages to work properly:

* [Python] - The Mycroft language
* [python-twitter] - A Twitter SDK made for Python
* [Facebook SDK for Python] -  A Facebook SDK made for Python
* [Selenium] - Using selenium threw a Mycroft skill called browser_service
* [fbchat] - Library that uses Selenium to send messages to facebook friends
* [Levenshtein] - In order to compare Strings

And of course Mycroft-Social-Network-Manager itself is open source with a [public repository][public-repo] on GitHub.



   [mycroftwebsite]: <https://mycroft.ai/>
   [public-repo]:<https://github.com/ldevalbray/mycroft-social-network-manager>
