#socket connects to the server
#time gets time for time stamps and does sleep
#os makes directories for logs, and gets the process ID
#sys is used to kill itself
#Thread is used for multi threading
#re is used for regex, for swear detect
#pickle is used to store the config, also scriptures
#pprint is used to view the config
#importlib is used to import modules on the fly, hopefully
#copy is used to copy the self.conf variable
import time, os, pickle
from threading import Thread
#from megahal import *
import re

from xml.dom import minidom
from datetime import datetime

from inc.commons import Commons
from Server import Server, ServerFactory
from PermissionMask import PermissionMask
from UserGroup import UserGroup
from FunctionDispatcher import FunctionDispatcher
from Function import Function

endl = Commons.mEndLine

class Hallo:
    mDefaultNick = "Hallo"
    mDefaultPrefix = False
    mDefaultFullName = "HalloBot HalloHost HalloServer :an irc bot by spangle"
    mOpen = False
    mServerFactory = None
    mPermissionMask = None
    mFunctionDispatcher = None
    mUserGroupList = {}
    mServerList = []

    def __init__(self):
        #Create ServerFactory
        self.mServerFactory = ServerFactory(self)
        self.mPermissionMask = PermissionMask()
        #load config
        self.loadFromXml()
        self.mOpen = True
        #TODO: manual FunctionDispatcher construction, user input
        if(self.mFunctionDispatcher is None):
            self.mFunctionDispatcher = FunctionDispatcher(set("Random","ServerControl"))
        #TODO: deprecate and remove this
        self.base_start()
        #If no servers, ask for a new server
        if(len(self.mServerList)==0):
            if(sum([server.getAutoConnect() for server in self.mServerList])==0):
                self.conf = self.manualServerConnect()
        #connect to autoconnect servers
        print('connecting to servers')
        for server in self.mServerList:
            if(server.getAutoConnect()):
                Thread(target=server.run).start()
        time.sleep(2)
        #main loop, sticks around throughout the running of the bot
        print('connected to all servers.')
        self.coreLoopTimeEvents()
    
    def coreLoopTimeEvents(self):
        'Runs a loop to keep hallo running, while calling time events with the FunctionDispatcher passive dispatcher'
        lastDateTime = datetime.now()
        while(self.mOpen):
            nowDateTime = datetime.now()
            if(nowDateTime.second!=lastDateTime.second):
                self.mFunctionDispatcher.dispatchPassive(Function.EVENT_SECOND,None,None,None,None)
            if(nowDateTime.minute!=lastDateTime.minute):
                self.mFunctionDispatcher.dispatchPassive(Function.EVENT_MINUTE,None,None,None,None)
            if(nowDateTime.hour!=lastDateTime.hour):
                self.mFunctionDispatcher.dispatchPassive(Function.EVENT_HOUR,None,None,None,None)
            if(nowDateTime.day!=lastDateTime.day):
                self.mFunctionDispatcher.dispatchPassive(Function.EVENT_DAY,None,None,None,None)
            lastDateTime = nowDateTime
            time.sleep(0.1)
        

    def loadFromXml(self):
        try:
            doc = minidom.parse("config/config.xml")
            self.mDefaultNick = doc.getElementsByTagName("default_nick")[0].firstChild.data
            self.mDefaultPrefix = doc.getElementsByTagName("default_prefix")[0].firstChild.data
            self.mDefaultFullName = doc.getElementsByTagName("default_full_name")[0].firstChild.data
            self.mFunctionDispatcher = FunctionDispatcher.fromXml(doc.getElementsByTagName("function_dispatcher")[0].toxml())
            serverListXml = doc.getElementsByTagName("server_list")[0]
            for serverXml in serverListXml.getElementsByTagName("server"):
                serverObject = self.mServerFactory.newServerFromXml(serverXml.toxml())
                self.addServer(serverObject)
            userGroupListXml = doc.getElementsByTagName("user_group_list")[0]
            for userGroupXml in userGroupListXml.getElementsByTagName("user_group"):
                userGroupObject = UserGroup.fromXml(userGroupXml.toxml())
                self.addUserGroup(userGroupObject)
            if(len(doc.getElementsByTagName("permission_mask"))!=0):
                self.mPermissionMask = PermissionMask.fromXml(doc.getElementsByTagName("permission_mask")[0].toxml())
            return
        except (FileNotFoundError, IOError):
            print("Error loading config")
            self.manualServerConnect()

    def saveToXml(self):
        doc = minidom.Document();
        #create root element
        root = doc.createElement("config")
        doc.appendChild(root)
        #create default_nick element
        defaultNickElement = doc.createElement("default_nick")
        defaultNickElement.appendChild(doc.createTextNode(self.mDefaultNick))
        root.appendChild(defaultNickElement)
        #create default_prefix element
        defaultPrefixElement = doc.createElement("default_prefix")
        defaultPrefixElement.appendChild(doc.createTextNode(self.mDefaultPrefix))
        root.appendChild(defaultPrefixElement)
        #create default_full_name element
        defaultFullNameElement = doc.createElement("default_full_name")
        defaultFullNameElement.appendChild(doc.createTextNode(self.mDefaultFullName))
        root.appendChild(defaultFullNameElement)
        #Create function dispatcher
        functionDispatcherElement = minidom.parse(self.mFunctionDispatcher.toXml()).firstChild
        root.appendChild(functionDispatcherElement)
        #create server list
        serverListElement = doc.createElement("server_list")
        for serverItem in self.mServerList:
            serverElement = minidom.parse(serverItem.toXml()).firstChild
            serverListElement.appendChild(serverElement)
        root.appendChild(serverListElement)
        #create user_group list
        userGroupListElement = doc.createElement("user_group_list")
        for userGroupName in self.mUserGroupList:
            userGroupElement = minidom.parse(self.mUserGroupList[userGroupName].toXml()).firstChild
            userGroupListElement.appendChild(userGroupElement)
        root.appendChild(userGroupListElement)
        #Create permission_mask element, if it's not empty.
        if(not self.mPermissionMask.isEmpty()):
            permissionMaskElement = minidom.parse(self.mPermissionMask.toXml()).firstChild
            root.appendChild(permissionMaskElement)
        #save XML
        doc.writexml(open("config/config.xml","w"),indent="  ",addindent="  ",newl="\n")
    
    def addUserGroup(self,userGroup):
        'Adds a new UserGroup to the UserGroup list'
        userGroupName = userGroup.getName()
        self.mUserGroupList[userGroupName] = userGroup
    
    def getUserGroupByName(self,userGroupName):
        'Returns the UserGroup with the specified name'
        if(userGroupName in self.mUserGroupList):
            return self.mUserGroupList[userGroupName]
        return None
    
    def removeUserGroupByName(self,userGroupName):
        'Removes a user group specified by name'
        del self.mUserGroupList[userGroupName]
        
    def addServer(self,server):
        #adds a new server to the server list
        self.mServerList += server
        
    def getServerByName(self,serverName):
        for server in self.mServerList:
            if(server.getName()==serverName):
                return server
        return None
    
    def removeServer(self,server):
        self.mServerList.remove(server)
        
    def removeServerByName(self,serverName):
        for server in self.mServerList:
            if(server.getName()==serverName):
                self.mServerList.remove(server)
                
    def close(self):
        'Shuts down the entire program'
        for server in self.mServerList:
            server.disconnect()
        self.mFunctionDispatcher.close()
        self.saveToXml()
        self.mOpen = False
        
    def rightsCheck(self,rightName):
        'Checks the value of the right with the specified name. Returns boolean'
        rightValue = self.mPermissionMask.getRight(rightName)
        #If PermissionMask contains that right, return it.
        if(rightValue in [True,False]):
            return rightValue
        #If it's a function right, go to default_function right
        if(rightName.startswith("function_")):
            return self.rightsCheck("default_function")
        #If default_function is not defined, define and return it as True
        if(rightName=="default_function"):
            self.mPermissionMask.setRight("default_function",True)
            return True
        else:
            #Else, define and return False
            self.mPermissionMask.setRight(rightName,False)
            return False
        
    def getDefaultNick(self):
        'Default nick getter'
        return self.mDefaultNick

    def setDefaultNick(self,defaultNick):
        'Default nick setter'
        self.mDefaultNick = defaultNick
        
    def getDefaultPrefix(self):
        'Default prefix getter'
        return self.mDefaultPrefix
    
    def setDefaultPrefix(self,defaultPrefix):
        'Default prefix setter'
        self.mDefaultPrefix = defaultPrefix
        
    def getDefaultFullName(self):
        'Default full name getter'
        return self.mDefaultFullName
    
    def setDefaultFullName(self,defaultFullName):
        'Default full name setter'
        self.mDefaultFullName = defaultFullName
    
    def getFunctionDispatcher(self):
        'Returns the FunctionDispatcher object'
        return self.mFunctionDispatcher
    
    def manualServerConnect(self):
        #TODO: add ability to connect to non-IRC servers
        print("No servers have been loaded or connected to. Please connect to an IRC server.")
        godNick = input("What nickname is the bot operator using? [deer-spangle]")
        godNick = godNick.replace(' ','')
        if(godNick==''):
            godNick = 'deer-spangle'
        serverAddr = input("What server should the bot connect to? [irc.freenode.net:6667]")
        serverAddr = serverAddr.replace(' ','')
        if(serverAddr==''):
            serverAddr = 'irc.freenode.net:6667'
        serverUrl = serverAddr.split(':')[0]
        serverPort = serverAddr.split(':')[1]
        serverMatch = re.match(r'([a-z\d\.-]+\.)?([a-z\d-]{1,63})\.([a-z]{2,3}\.[a-z]{2}|[a-z]{2,6})',serverUrl,re.I)
        serverName = serverMatch.group(2)
        #Create the server object
        newServer = Server(self,serverName,serverUrl,serverPort)
        #Add new server to server list
        self.addServer(newServer)
        #Save XML
        self.saveToXml()
        #TODO: remove all this crap
        self.conf['server'] = {}
        self.conf['server'][serverName] = {}
        self.conf['server'][serverName]['ops'] = []
        self.conf['server'][serverName]['gods'] = [godNick]
        self.conf['server'][serverName]['address'] = serverName
        self.conf['server'][serverName]['nick'] = self.mDefaultNick
        self.conf['server'][serverName]['full_name'] = self.mDefaultFullName
        self.conf['server'][serverName]['pass'] = False
        self.conf['server'][serverName]['port'] = serverPort
        self.conf['server'][serverName]['channel'] = {}
        self.conf['server'][serverName]['admininform'] = []
        self.conf['server'][serverName]['pingdiff'] = 600
        self.conf['server'][serverName]['connected'] = True
        print("Config file created.")
        #TODO: remove this
        pickle.dump(self.conf,open(self.configfile,"wb"))
        print("Config file saved.")

    def base_start(self):
        #TODO: remove configfile loading
        try:
            self.conf = pickle.load(open("store/config.p","rb"))
        except EOFError:
            #TODO: remove all this crap
            self.conf = {}
            self.conf['function'] = {}
            self.conf['function']['default'] = {}
            self.conf['function']['default']['disabled'] = False
            self.conf['function']['default']['listed_to'] = 'user'
            self.conf['function']['default']['max_run_time'] = 180
            self.conf['function']['default']['privmsg'] = True
            self.conf['function']['default']['repair'] = False
            self.conf['function']['default']['return_to'] = 'channel'
            self.conf['function']['default']['time_delay'] = 0
            self.conf['nickserv'] = {}
            self.conf['nickserv']['online'] = ['lastseen:now','isonlinefrom:','iscurrentlyonline','nosuchnick','userseen:now']
            self.conf['nickserv']['registered'] = ['registered:']
        self.megahal = {}
        self.core = {}
        self.core['server'] = {}
        self.core['function'] = {}


#######################################################
#######EVERYTHING BELOW HERE WILL NEED BREAKING INTO OTHER OBJECTS
#######################################################


    def base_addlog(self,msg,destination):
        # log a message for future reference
        if(not os.path.exists('logs/')):
            os.makedirs('logs/')
        if(not os.path.exists('logs/' + destination[0])):
            os.makedirs('logs/' + destination[0])
        if(not os.path.exists('logs/' + destination[0] + '/' + destination[1])):
            os.makedirs('logs/' + destination[0] + '/' + destination[1])
        # date is the file name
        filename = str(time.gmtime()[0]).rjust(4,'0') + '-' + str(time.gmtime()[1]).rjust(2,'0') + '-' + str(time.gmtime()[2]).rjust(2,'0') + '.txt'
        # open and write the message
        log = open('logs/' + destination[0] + '/' + destination[1] + '/' + filename, 'a')
        log.write(msg.encode('ascii','ignore').decode() + '\n')
        log.close()

if __name__ == '__main__':
    Hallo()
#    ircbot().run(raw_input('network: '), raw_input('nick: '), [raw_input('channel: ')])
