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

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

sys.path.append(abspath(dirname(__file__)))
Facebook = __import__('fb').Facebook
Twitter = __import__('tw').Twitter

__author__ = 'ldevalbray'

logger = getLogger(abspath(__file__).split('/')[-2])

class SocialMediaSkill(MycroftSkill):

    def __init__(self):
        super(SocialMediaSkill, self).__init__(name="SocialMediaSkill")
        self.FB = 'facebook'
        self.TW = 'twitter'
        # self.fb = Facebook()
        # self.tw = Twitter()

    def initialize(self):
        self.load_data_files(dirname(__file__))

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


def create_skill():
    return SocialMediaSkill()
