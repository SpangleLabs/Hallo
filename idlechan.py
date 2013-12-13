#import random
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
        else:
            return '*tumbleweed*'

    def fnn_chat_to_s(self,args,client,destination):
        'chats to _S'
        return "_S: SO, HOW ARE THINGS?"

