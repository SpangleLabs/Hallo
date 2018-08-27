import unittest

from Events import EventMessage
from Server import Server
from test.TestBase import TestBase


class FinnBotTest(TestBase, unittest.TestCase):
    def test_aribot_simple(self):
        valid = ["|:", "After hearing you say that, I don't think we can ever be friends",
                 "Brb, cutting down a forest", "Can't answer, I'm shaving and it'll take all day",
                 "Can't hear you over all this atheism!",
                 "Can this wait until after i've listened to this song 100 times on repeat?",
                 "Could use less degrees", "Don't want to hear it, too busy complaining about the tap water",
                 "Goony goon goon", "Hang on, I have to help some micronationalist",
                 "Hey guys, check out my desktop: http://hallo.dr-spangle.com/DESKTOP.PNG",
                 "If we get into a fight, I'll pick you up and run away",
                 "I happen to be an expert on this subject", "I think I've finished constructing a hate engine",
                 "It's about time for me to play through adom again", "It's kind of hard to type while kneeling",
                 "I wish I could answer, but i'm busy redditing", "*lifeless stare*", "Lol, perl",
                 "Lol, remember when i got eli to play crawl for a week?", "Needs moar haskell",
                 "NP: Bad Religion - whatever song",
                 "Remember that thing we were going to do? Now I don't want to do it", "Smells like Oulu",
                 "Some Rahikkala is getting married, you are not invited",
                 "That blows, but I cannot relate to your situation", "This somehow reminds me of my army days",
                 "Whatever, if you'll excuse me, i'm gonna bike 50 kilometers",
                 "You guys are things that say things", "You're under arrest for having too much fun",
                 "I have found a new favourite thing to hate"]
        for _ in range(10):
            self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "finnbot"))
            data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
            line = data[0][0][:-1] if data[0][0][-1] == "." else data[0][0]
            assert line in valid, "Invalid quote returned."
