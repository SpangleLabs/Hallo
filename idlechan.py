import random
#import base64
#import urllib.request, urllib.error, urllib.parse
#import time
#import re
#import math
#from PIL import Image
#import io
#import pickle
#import euler
#import hallobase
#import threading
#import json
#import difflib
#import re
#import html.parser



endl = '\r\n'
class idlechan():
    def fnn_idlechan(self,args,client,destination):
        # SPANGLE ADDED THIS, should do things in channels, once they've been idle for a set amount of time.
        if(args.lower()=='chat to _s'):
            return idlechan.fnn_chat_to_s(self,args,client,destination)
        elif(args.lower()=='deer'):
            return 'deer deer deer.' 
        else:
            return '*tumbleweed*'

    def fnn_chat_to_s(self,args,client,destination):
        'chats to _S'
        messages = ['so, how are things?','is your end of the world holding up ok?',"let's talk about deer!","boop","beep","I'll be honest, this place is dead","Fuck snow","I guess everyone's asleep","clap... clap... *clap*","I'm watching you, robot.","What do you think of that D000242 guy?","What do you think of that spangle kid?","Butts.","I choose you!","How old are you in milli-Americas?"]
   #     messages.append("fuck deer, dragons are better!")
   #     messages.append("What's with all the deer-rape?")
        randmessage = messages[random.randint(0,len(messages)-1)]
        return "_S: " + randmessage

