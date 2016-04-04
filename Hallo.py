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
        self.load_from_xml()
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
                self.manual_server_connect()
        # Connect to auto-connect servers
        print('connecting to servers')
        for server in self.mServerList:
            if server.getAutoConnect():
                Thread(target=server.run).start()
        time.sleep(2)
        # Main loop, sticks around throughout the running of the bot
        print('connected to all servers.')
        self.core_loop_time_events()

    def core_loop_time_events(self):
        """
        Runs a loop to keep hallo running, while calling time events with the FunctionDispatcher passive dispatcher
        """
        last_date_time = datetime.now()
        while self.mOpen:
            now_date_time = datetime.now()
            if now_date_time.second != last_date_time.second:
                self.mFunctionDispatcher.dispatchPassive(Function.EVENT_SECOND, None, None, None, None)
            if now_date_time.minute != last_date_time.minute:
                self.mFunctionDispatcher.dispatchPassive(Function.EVENT_MINUTE, None, None, None, None)
            if now_date_time.hour != last_date_time.hour:
                self.mFunctionDispatcher.dispatchPassive(Function.EVENT_HOUR, None, None, None, None)
            if now_date_time.day != last_date_time.day:
                self.mFunctionDispatcher.dispatchPassive(Function.EVENT_DAY, None, None, None, None)
            last_date_time = now_date_time
            time.sleep(0.1)

    def load_from_xml(self):
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
        user_group_list_xml = root.find("user_group_list")
        for user_group_xml in user_group_list_xml.findall("user_group"):
            user_group_obj = UserGroup.fromXml(ElementTree.tostring(user_group_xml), self)
            self.add_user_group(user_group_obj)
        server_list_xml = root.find("server_list")
        for server_xml in server_list_xml.findall("server"):
            server_obj = self.mServerFactory.newServerFromXml(ElementTree.tostring(server_xml))
            self.add_server(server_obj)
        if root.find("permission_mask") is not None:
            self.mPermissionMask = PermissionMask.fromXml(ElementTree.tostring(root.find("permission_mask")))
        api_key_list_xml = root.find("api_key_list")
        for api_key_xml in api_key_list_xml.findall("api_key"):
            api_key_name = api_key_xml.findtext("name")
            api_key_key = api_key_xml.findtext("key")
            self.add_api_key(api_key_name, api_key_key)
        return

    def save_to_xml(self):
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
        default_nick_elem = doc.createElement("default_nick")
        default_nick_elem.appendChild(doc.createTextNode(self.mDefaultNick))
        root.appendChild(default_nick_elem)
        # Create default_prefix element
        if self.mDefaultPrefix is not None:
            default_prefix_elem = doc.createElement("default_prefix")
            if self.mDefaultPrefix is False:
                default_prefix_elem.appendChild(doc.createTextNode("0"))
            else:
                default_prefix_elem.appendChild(doc.createTextNode(self.mDefaultPrefix))
            root.appendChild(default_prefix_elem)
        # Create default_full_name element
        default_full_name_elem = doc.createElement("default_full_name")
        default_full_name_elem.appendChild(doc.createTextNode(self.mDefaultFullName))
        root.appendChild(default_full_name_elem)
        # Create function dispatcher
        function_dispatcher_elem = minidom.parseString(self.mFunctionDispatcher.toXml()).firstChild
        root.appendChild(function_dispatcher_elem)
        # Create server list
        server_list_elem = doc.createElement("server_list")
        for server_elem in self.mServerList:
            server_xml = minidom.parseString(server_elem.toXml()).firstChild
            server_list_elem.appendChild(server_xml)
        root.appendChild(server_list_elem)
        # Create user_group list
        user_group_list_elem = doc.createElement("user_group_list")
        for user_group_name in self.mUserGroupList:
            user_group_elem = minidom.parseString(self.mUserGroupList[user_group_name].toXml()).firstChild
            user_group_list_elem.appendChild(user_group_elem)
        root.appendChild(user_group_list_elem)
        # Create permission_mask element, if it's not empty.
        if not self.mPermissionMask.isEmpty():
            permission_mask_elem = minidom.parseString(self.mPermissionMask.toXml()).firstChild
            root.appendChild(permission_mask_elem)
        # Save api key list
        api_key_list_elem = doc.createElement("api_key_list")
        for api_key_name in self.mApiKeys:
            api_key_elem = doc.createElement("api_key")
            api_key_name_elem = doc.createElement("name")
            api_key_name_elem.appendChild(doc.createTextNode(api_key_name))
            api_key_elem.appendChild(api_key_name_elem)
            api_key_key_elem = doc.createElement("key")
            api_key_key_elem.appendChild(doc.createTextNode(self.mApiKeys[api_key_name]))
            api_key_elem.appendChild(api_key_key_elem)
            api_key_list_elem.appendChild(api_key_elem)
        root.appendChild(api_key_list_elem)
        # Save XML
        doc.writexml(open("config/config.xml", "w"), addindent="\t", newl="\r\n")

    def add_user_group(self, user_group):
        """
        Adds a new UserGroup to the UserGroup list
        :param user_group: UserGroup to add to the hallo object's list of user groups
        """
        user_group_name = user_group.getName()
        self.mUserGroupList[user_group_name] = user_group

    def get_user_group_by_name(self, user_group_name):
        """
        Returns the UserGroup with the specified name
        :param user_group_name: Name of user group to search for
        :return: User Group matching specified name, or None
        """
        if user_group_name in self.mUserGroupList:
            return self.mUserGroupList[user_group_name]
        return None

    def remove_user_group_by_name(self, user_group_name):
        """
        Removes a user group specified by name
        :param user_group_name: Name of the user group to remove from list
        """
        del self.mUserGroupList[user_group_name]

    def add_server(self, server):
        """
        Adds a new server to the server list
        :param server: Server to add to Hallo's list of servers
        """
        self.mServerList.append(server)

    def get_server_by_name(self, server_name):
        """
        Returns a server matching the given name
        :param server_name: name of the server to search for
        :return: Server matching specified name of None
        """
        for server in self.mServerList:
            if server.getName().lower() == server_name.lower():
                return server
        return None

    def get_server_list(self):
        """Returns the server list for hallo"""
        return self.mServerList

    def remove_server(self, server):
        self.mServerList.remove(server)

    def remove_server_by_name(self, server_name):
        for server in self.mServerList:
            if server.getName() == server_name:
                self.mServerList.remove(server)

    def close(self):
        """Shuts down the entire program"""
        for server in self.mServerList:
            server.disconnect()
        self.mFunctionDispatcher.close()
        self.save_to_xml()
        self.mOpen = False

    def rights_check(self, right_name):
        """
        Checks the value of the right with the specified name. Returns boolean
        :param right_name: name of the user right to search for
        :return: Boolean, whether or not the specified right is given
        """
        right_value = self.mPermissionMask.getRight(right_name)
        # If PermissionMask contains that right, return it.
        if right_value in [True, False]:
            return right_value
        # If it's a function right, go to default_function right
        if right_name.startswith("function_"):
            return self.rights_check("default_function")
        # If default_function is not defined, define and return it as True
        if right_name == "default_function":
            self.mPermissionMask.setRight("default_function", True)
            return True
        else:
            # Else, define and return False
            self.mPermissionMask.setRight(right_name, False)
            return False

    def get_default_nick(self):
        """Default nick getter"""
        return self.mDefaultNick

    def set_default_nick(self, default_nick):
        """
        Default nick setter
        :param default_nick: The new default nick to use on all new servers
        """
        self.mDefaultNick = default_nick

    def get_default_prefix(self):
        """Default prefix getter"""
        return self.mDefaultPrefix

    def set_default_prefix(self, default_prefix):
        """
        Default prefix setter
        :param default_prefix: Default prefix to use for commands addressed to the bot
        """
        self.mDefaultPrefix = default_prefix

    def get_default_full_name(self):
        """Default full name getter"""
        return self.mDefaultFullName

    def set_default_full_name(self, default_full_name):
        """
        Default full name setter
        :param default_full_name: Default full name to use on all new server connections
        """
        self.mDefaultFullName = default_full_name

    def get_permission_mask(self):
        return self.mPermissionMask

    def get_function_dispatcher(self):
        """Returns the FunctionDispatcher object"""
        return self.mFunctionDispatcher

    def get_logger(self):
        """Returns the Logger object"""
        return self.mLogger

    def get_printer(self):
        """Returns the Printer object"""
        return self.mPrinter

    def add_api_key(self, name, key):
        """
        Adds an api key to the list, or overwrites one.
        :param name: Name of the API to add
        :param key: The actual API key to use
        """
        self.mApiKeys[name] = key

    def get_api_key(self, name):
        """
        Returns a specified api key.
        :param name: Name of the API key to retrieve
        """
        if name in self.mApiKeys:
            return self.mApiKeys[name]
        return None

    def manual_server_connect(self):
        # TODO: add ability to connect to non-IRC servers
        print("No servers have been loaded or connected to. Please connect to an IRC server.")
        # godNick = input("What nickname is the bot operator using? [deer-spangle] ")
        # godNick = godNick.replace(' ', '')
        # if godNick == '':
        #     godNick = 'deer-spangle'
        # TODO: do something with godNick
        server_addr = input("What server should the bot connect to? [irc.freenode.net:6667] ")
        server_addr = server_addr.replace(' ', '')
        if server_addr == '':
            server_addr = 'irc.freenode.net:6667'
        server_url = server_addr.split(':')[0]
        server_port = int(server_addr.split(':')[1])
        server_match = re.match(r'([a-z\d\.-]+\.)?([a-z\d-]{1,63})\.([a-z]{2,3}\.[a-z]{2}|[a-z]{2,6})', server_url,
                                re.I)
        server_name = server_match.group(2)
        # Create the server object
        new_server = ServerIRC(self, server_name, server_url, server_port)
        # Add new server to server list
        self.add_server(new_server)
        # Save XML
        self.save_to_xml()
        print("Config file saved.")


if __name__ == '__main__':
    Hallo()
