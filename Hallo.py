#!/usr/bin/env python3
import time
from threading import Thread
import re
from xml.dom import minidom
from xml.etree import ElementTree
from datetime import datetime
from Server import ServerIRC, ServerFactory
from PermissionMask import PermissionMask
from UserGroup import UserGroup
from FunctionDispatcher import FunctionDispatcher
from Function import Function
from inc.Logger import Logger
from inc.Printer import Printer
from inc.commons import Commons


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
    mApiKeys = None

    def __init__(self):
        self.mUserGroupList = {}
        self.mServerList = []
        self.mLogger = Logger(self)
        self.mPrinter = Printer(self)
        self.mApiKeys = {}
        # Create ServerFactory
        self.mServerFactory = ServerFactory(self)
        self.mPermissionMask = PermissionMask()
        # Load config
        self.loadFromXml()
        self.mOpen = True
        # TODO: manual FunctionDispatcher construction, user input
        if self.mFunctionDispatcher is None:
            self.mFunctionDispatcher = FunctionDispatcher(
                {"ChannelControl",
                 "Convert",
                 "HalloControl",
                 "Lookup",
                 "Math",
                 "PermissionControl",
                 "Random",
                 "ServerControl"},
                self)
        # If no servers, ask for a new server
        if len(self.mServerList) == 0:
            if sum([server.getAutoConnect() for server in self.mServerList]) == 0:
                self.manualServerConnect()
        # Connect to auto-connect servers
        print('connecting to servers')
        for server in self.mServerList:
            if server.getAutoConnect():
                Thread(target=server.run).start()
        time.sleep(2)
        # Main loop, sticks around throughout the running of the bot
        print('connected to all servers.')
        self.coreLoopTimeEvents()

    def coreLoopTimeEvents(self):
        """
        Runs a loop to keep hallo running, while calling time events with the FunctionDispatcher passive dispatcher
        """
        lastDateTime = datetime.now()
        while self.mOpen:
            nowDateTime = datetime.now()
            if nowDateTime.second != lastDateTime.second:
                self.mFunctionDispatcher.dispatchPassive(Function.EVENT_SECOND, None, None, None, None)
            if nowDateTime.minute != lastDateTime.minute:
                self.mFunctionDispatcher.dispatchPassive(Function.EVENT_MINUTE, None, None, None, None)
            if nowDateTime.hour != lastDateTime.hour:
                self.mFunctionDispatcher.dispatchPassive(Function.EVENT_HOUR, None, None, None, None)
            if nowDateTime.day != lastDateTime.day:
                self.mFunctionDispatcher.dispatchPassive(Function.EVENT_DAY, None, None, None, None)
            lastDateTime = nowDateTime
            time.sleep(0.1)

    def loadFromXml(self):
        try:
            doc = ElementTree.parse("config/config.xml")
        except (OSError, IOError):
            print("No current config, loading from default.")
            doc = ElementTree.parse("config/config-default.xml")
        root = doc.getroot()
        self.mDefaultNick = root.findtext("default_nick")
        self.mDefaultPrefix = Commons.stringFromFile(root.findtext("default_prefix"))
        self.mDefaultFullName = root.findtext("default_full_name")
        self.mFunctionDispatcher = FunctionDispatcher.fromXml(ElementTree.tostring(root.find("function_dispatcher")),
                                                              self)
        userGroupListXml = root.find("user_group_list")
        for userGroupXml in userGroupListXml.findall("user_group"):
            userGroupObject = UserGroup.fromXml(ElementTree.tostring(userGroupXml), self)
            self.addUserGroup(userGroupObject)
        serverListXml = root.find("server_list")
        for serverXml in serverListXml.findall("server"):
            serverObject = self.mServerFactory.newServerFromXml(ElementTree.tostring(serverXml))
            self.addServer(serverObject)
        if root.find("permission_mask") is not None:
            self.mPermissionMask = PermissionMask.fromXml(ElementTree.tostring(root.find("permission_mask")))
        apiKeyListXml = root.find("api_key_list")
        for apiKeyXml in apiKeyListXml.findall("api_key"):
            apiKeyName = apiKeyXml.findtext("name")
            apiKeyKey = apiKeyXml.findtext("key")
            self.addApiKey(apiKeyName, apiKeyKey)
        return

    def saveToXml(self):
        # Create document, with DTD
        docimp = minidom.DOMImplementation()
        doctype = docimp.createDocumentType(
            qualifiedName='config',
            publicId='',
            systemId='config.dtd',
        )
        doc = docimp.createDocument(None, 'config', doctype)
        # Get root element
        root = doc.getElementsByTagName("config")[0]
        # Create default_nick element
        defaultNickElement = doc.createElement("default_nick")
        defaultNickElement.appendChild(doc.createTextNode(self.mDefaultNick))
        root.appendChild(defaultNickElement)
        # Create default_prefix element
        if self.mDefaultPrefix is not None:
            defaultPrefixElement = doc.createElement("default_prefix")
            if self.mDefaultPrefix is False:
                defaultPrefixElement.appendChild(doc.createTextNode("0"))
            else:
                defaultPrefixElement.appendChild(doc.createTextNode(self.mDefaultPrefix))
            root.appendChild(defaultPrefixElement)
        # Create default_full_name element
        defaultFullNameElement = doc.createElement("default_full_name")
        defaultFullNameElement.appendChild(doc.createTextNode(self.mDefaultFullName))
        root.appendChild(defaultFullNameElement)
        # Create function dispatcher
        functionDispatcherElement = minidom.parseString(self.mFunctionDispatcher.toXml()).firstChild
        root.appendChild(functionDispatcherElement)
        # Create server list
        serverListElement = doc.createElement("server_list")
        for serverItem in self.mServerList:
            serverElement = minidom.parseString(serverItem.toXml()).firstChild
            serverListElement.appendChild(serverElement)
        root.appendChild(serverListElement)
        # Create user_group list
        userGroupListElement = doc.createElement("user_group_list")
        for userGroupName in self.mUserGroupList:
            userGroupElement = minidom.parseString(self.mUserGroupList[userGroupName].toXml()).firstChild
            userGroupListElement.appendChild(userGroupElement)
        root.appendChild(userGroupListElement)
        # Create permission_mask element, if it's not empty.
        if not self.mPermissionMask.isEmpty():
            permissionMaskElement = minidom.parseString(self.mPermissionMask.toXml()).firstChild
            root.appendChild(permissionMaskElement)
        # Save api key list
        apiKeyListElement = doc.createElement("api_key_list")
        for apiKeyName in self.mApiKeys:
            apiKeyElement = doc.createElement("api_key")
            apiKeyNameElement = doc.createElement("name")
            apiKeyNameElement.appendChild(doc.createTextNode(apiKeyName))
            apiKeyElement.appendChild(apiKeyNameElement)
            apiKeyKeyElement = doc.createElement("key")
            apiKeyKeyElement.appendChild(doc.createTextNode(self.mApiKeys[apiKeyName]))
            apiKeyElement.appendChild(apiKeyKeyElement)
            apiKeyListElement.appendChild(apiKeyElement)
        root.appendChild(apiKeyListElement)
        # Save XML
        doc.writexml(open("config/config.xml", "w"), addindent="\t", newl="\r\n")

    def addUserGroup(self, userGroup):
        """
        Adds a new UserGroup to the UserGroup list
        :param userGroup: UserGroup to add to the hallo object's list of user groups
        """
        userGroupName = userGroup.getName()
        self.mUserGroupList[userGroupName] = userGroup

    def getUserGroupByName(self, userGroupName):
        """
        Returns the UserGroup with the specified name
        :param userGroupName: Name of user group to search for
        :return: User Group matching specified name, or None
        """
        if userGroupName in self.mUserGroupList:
            return self.mUserGroupList[userGroupName]
        return None

    def removeUserGroupByName(self, userGroupName):
        """
        Removes a user group specified by name
        :param userGroupName: Name of the user group to remove from list
        """
        del self.mUserGroupList[userGroupName]

    def addServer(self, server):
        """
        Adds a new server to the server list
        :param server: Server to add to Hallo's list of servers
        """
        self.mServerList.append(server)

    def getServerByName(self, serverName):
        """
        Returns a server matching the given name
        :param serverName: name of the server to search for
        :return: Server matching specified name of None
        """
        for server in self.mServerList:
            if server.getName().lower() == serverName.lower():
                return server
        return None

    def getServerList(self):
        """Returns the server list for hallo"""
        return self.mServerList

    def removeServer(self, server):
        self.mServerList.remove(server)

    def removeServerByName(self, serverName):
        for server in self.mServerList:
            if server.getName() == serverName:
                self.mServerList.remove(server)

    def close(self):
        """Shuts down the entire program"""
        for server in self.mServerList:
            server.disconnect()
        self.mFunctionDispatcher.close()
        self.saveToXml()
        self.mOpen = False

    def rightsCheck(self, rightName):
        """
        Checks the value of the right with the specified name. Returns boolean
        :param rightName: name of the user right to search for
        :return: Boolean, whether or not the specified right is given
        """
        rightValue = self.mPermissionMask.getRight(rightName)
        # If PermissionMask contains that right, return it.
        if rightValue in [True, False]:
            return rightValue
        # If it's a function right, go to default_function right
        if rightName.startswith("function_"):
            return self.rightsCheck("default_function")
        # If default_function is not defined, define and return it as True
        if rightName == "default_function":
            self.mPermissionMask.setRight("default_function", True)
            return True
        else:
            # Else, define and return False
            self.mPermissionMask.setRight(rightName, False)
            return False

    def getDefaultNick(self):
        """Default nick getter"""
        return self.mDefaultNick

    def setDefaultNick(self, defaultNick):
        """
        Default nick setter
        :param defaultNick: The new default nick to use on all new servers
        """
        self.mDefaultNick = defaultNick

    def getDefaultPrefix(self):
        """Default prefix getter"""
        return self.mDefaultPrefix

    def setDefaultPrefix(self, defaultPrefix):
        """
        Default prefix setter
        :param defaultPrefix: Default prefix to use for commands addressed to the bot
        """
        self.mDefaultPrefix = defaultPrefix

    def getDefaultFullName(self):
        """Default full name getter"""
        return self.mDefaultFullName

    def setDefaultFullName(self, defaultFullName):
        """
        Default full name setter
        :param defaultFullName: Default full name to use on all new server connections
        """
        self.mDefaultFullName = defaultFullName

    def getPermissionMask(self):
        return self.mPermissionMask

    def getFunctionDispatcher(self):
        """Returns the FunctionDispatcher object"""
        return self.mFunctionDispatcher

    def getLogger(self):
        """Returns the Logger object"""
        return self.mLogger

    def getPrinter(self):
        """Returns the Printer object"""
        return self.mPrinter

    def addApiKey(self, name, key):
        """
        Adds an api key to the list, or overwrites one.
        :param name: Name of the API to add
        :param key: The actual API key to use
        """
        self.mApiKeys[name] = key

    def getApiKey(self, name):
        """
        Returns a specified api key.
        :param name: Name of the API key to retrieve
        """
        if name in self.mApiKeys:
            return self.mApiKeys[name]
        return None

    def manualServerConnect(self):
        # TODO: add ability to connect to non-IRC servers
        print("No servers have been loaded or connected to. Please connect to an IRC server.")
        # godNick = input("What nickname is the bot operator using? [deer-spangle] ")
        # godNick = godNick.replace(' ', '')
        # if godNick == '':
        #     godNick = 'deer-spangle'
        # TODO: do something with godNick
        serverAddr = input("What server should the bot connect to? [irc.freenode.net:6667] ")
        serverAddr = serverAddr.replace(' ', '')
        if serverAddr == '':
            serverAddr = 'irc.freenode.net:6667'
        serverUrl = serverAddr.split(':')[0]
        serverPort = int(serverAddr.split(':')[1])
        serverMatch = re.match(r'([a-z\d\.-]+\.)?([a-z\d-]{1,63})\.([a-z]{2,3}\.[a-z]{2}|[a-z]{2,6})', serverUrl, re.I)
        serverName = serverMatch.group(2)
        # Create the server object
        newServer = ServerIRC(self, serverName, serverUrl, serverPort)
        # Add new server to server list
        self.addServer(newServer)
        # Save XML
        self.saveToXml()
        print("Config file saved.")


if __name__ == '__main__':
    Hallo()
