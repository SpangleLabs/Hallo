#socket connects to the server
#time gets time for time stamps and does sleep
#os makes directories for logs, and gets the process ID
#sys is used to kill itself
#Thread is used for multi threading
#re is used for regex, for swear detect
import time, os
from threading import Thread
#from megahal import *
import re

from xml.dom import minidom
from datetime import datetime

from Server import Server, ServerFactory
from PermissionMask import PermissionMask
from UserGroup import UserGroup
from FunctionDispatcher import FunctionDispatcher
from Function import Function
from inc.Logger import Logger
from inc.Printer import Printer

class Hallo:
    mDefaultNick = "Hallo"
    mDefaultPrefix = False
    mDefaultFullName = "HalloBot HalloHost HalloServer :an irc bot by spangle"
    mOpen = False
    mServerFactory = None
    mPermissionMask = None
    mFunctionDispatcher = None
    mUserGroupList = None
    mServerList = None
    mLogger = None
    mPrinter = None

    def __init__(self):
        self.mUserGroupList = {}
        self.mServerList = []
        self.mLogger = Logger(self)
        self.mPrinter = Printer(self)
        #Create ServerFactory
        self.mServerFactory = ServerFactory(self)
        self.mPermissionMask = PermissionMask()
        #load config
        self.loadFromXml()
        self.mOpen = True
        #TODO: manual FunctionDispatcher construction, user input
        if(self.mFunctionDispatcher is None):
            self.mFunctionDispatcher = FunctionDispatcher(set("ChannelControl","Convert","HalloControl","Lookup","Math","PermissionControl","Random","ServerControl"))
        #If no servers, ask for a new server
        if(len(self.mServerList)==0):
            if(sum([server.getAutoConnect() for server in self.mServerList])==0):
                self.manualServerConnect()
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
        except (OSError, IOError):
            print("Error loading config")
            self.manualServerConnect()

    def saveToXml(self):
        #Create document, with DTD
        docimp = minidom.DOMImplementation()
        doctype = docimp.createDocumentType(
            qualifiedName='config',
            publicId='', 
            systemId='config.dtd',
        )
        doc = docimp.createDocument(None, 'config', doctype)
        #get root element
        root = doc.getElementsByTagName("config")[0]
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
        doc.writexml(open("config/config.xml","w"),addindent="\t",newl="\r\n")
    
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
            if(server.getName().lower()==serverName.lower()):
                return server
        return None
    
    def getServerList(self):
        'Returns the server list for hallo'
        return self.mServerList
    
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
    
    def getPermissionMask(self):
        return self.mPermissionMask
    
    def getFunctionDispatcher(self):
        'Returns the FunctionDispatcher object'
        return self.mFunctionDispatcher
    
    def getLogger(self):
        'Returns the Logger object'
        return self.mLogger
    
    def getPrinter(self):
        'Returns the Printer object'
        return self.mPrinter
    
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
        print("Config file saved.")

if __name__ == '__main__':
    Hallo()
