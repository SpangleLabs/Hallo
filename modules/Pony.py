from Function import Function
import random
from xml.dom import minidom
from inc.commons import Commons

class PonyEpisode(Function):
    '''
    Ouija board function. "Ouija board" is copyright Hasbro.
    '''
    #Name for use in help listing
    mHelpName = "pony eposide"
    #Names which can be used to address the function
    mNames = set(["pony episode","ponyep","pony ep","mlp episode","episode pony","random pony episode","random mlp episode"])
    #Help documentation, if it's just a single line, can be set here
    mHelpDocs = "Chooses a pony episode to watch at random. Format: \"pony_ep\" to pick a random pony episode, \"pony_ep song\" to pick a random pony episode which includes a song."
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def run(self,line,userObject,destinationObject=None):
        doc = minidom.parse("store/pony_episodes.xml")
        ponyEpisodesListXml = doc.getElementsByTagName("pony_episodes")[0]
        numEpisodes = len(ponyEpisodesListXml.getElementsByTagName("pony_episode"))
        episodeList = []
        songList = []
        for ponyEpisodeXml in ponyEpisodesListXml.getElementsByTagName("pony_episode"):
            episodeDict = {}
            episodeDict['name'] = ponyEpisodeXml.getElementsByTagName("name")[0].firstChild.data
            episodeDict['full_code'] = ponyEpisodeXml.getElementsByTagName("full_code")[0].firstChild.data
            if(Commons.stringToBool(ponyEpisodeXml.getElementsByTagName("song")[0].firstChild.data)):
                songList.append(episodeDict)
            episodeList.append(episodeDict)
        if(line.strip().lower()!="song"):
            numEpisodes = len(episodeList)
            rand = random.randint(0,numEpisodes-1)
            episode = episodeList[rand]
        else:
            numEpisodes = len(songList)
            rand = random.randint(0,numEpisodes-1)
            episode = songList[rand]
        return "You should choose: " + episode['full_code'] + " - " + episode['name'] + "."
    
    
    
    
    
    