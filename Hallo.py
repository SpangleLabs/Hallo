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

    def __init__(self):
        self.default_nick = "Hallo"
        self.default_prefix = False
        self.default_full_name = "HalloBot HalloHost HalloServer :an irc bot by spangle"
        self.open = False
        self.user_list_list = {}
        self.server_list = []
        self.logger = Logger(self)
        self.printer = Printer(self)
        self.api_key_list = {}
        # Create ServerFactory
        self.server_factory = ServerFactory(self)
        self.permission_mask = PermissionMask()
        # TODO: manual FunctionDispatcher construction, user input?
        self.function_dispatcher = FunctionDispatcher({"ChannelControl", "Convert", "HalloControl", "Lookup", "Math",
                                                       "PermissionControl", "Random", "ServerControl"}, self)

    def start(self):
        # If no servers, ask for a new server
        if len(self.server_list) == 0:
            if sum([server.get_auto_connect() for server in self.server_list]) == 0:
                self.manual_server_connect()
        # Connect to auto-connect servers
        print('connecting to servers')  # TODO: remove/replace this. Probably dump in Printer somewhere
        for server in self.server_list:
            if server.get_auto_connect():
                Thread(target=server.run).start()
        self.open = True
        count = 0
        while all(not server.open for server in self.server_list if server.get_auto_connect()):
            time.sleep(0.1)
            count += 1
            if count > 600:
                self.open = False
                print("No servers managed to connect in 60 seconds.")
                break
        # Main loop, sticks around throughout the running of the bot
        print('connected to all servers.')  # TODO: remove/replace this. Probably dump in Printer somewhere
        self.core_loop_time_events()

    def core_loop_time_events(self):
        """
        Runs a loop to keep hallo running, while calling time events with the FunctionDispatcher passive dispatcher
        """
        last_date_time = datetime.now()
        while self.open:
            now_date_time = datetime.now()
            if now_date_time.second != last_date_time.second:
                self.function_dispatcher.dispatch_passive(Function.EVENT_SECOND, None, None, None, None)
            if now_date_time.minute != last_date_time.minute:
                self.function_dispatcher.dispatch_passive(Function.EVENT_MINUTE, None, None, None, None)
            if now_date_time.hour != last_date_time.hour:
                self.function_dispatcher.dispatch_passive(Function.EVENT_HOUR, None, None, None, None)
            if now_date_time.day != last_date_time.day:
                self.function_dispatcher.dispatch_passive(Function.EVENT_DAY, None, None, None, None)
            last_date_time = now_date_time
            time.sleep(0.1)

    @staticmethod
    def load_from_xml():
        try:
            doc = ElementTree.parse("config/config.xml")
        except (OSError, IOError):
            print("No current config, loading from default.")
            doc = ElementTree.parse("config/config-default.xml")
        new_hallo = Hallo()
        root = doc.getroot()
        new_hallo.default_nick = root.findtext("default_nick")
        new_hallo.default_prefix = Commons.string_from_file(root.findtext("default_prefix"))
        new_hallo.default_full_name = root.findtext("default_full_name")
        new_hallo.function_dispatcher = FunctionDispatcher.from_xml(
            ElementTree.tostring(root.find("function_dispatcher")), new_hallo)
        user_group_list_xml = root.find("user_group_list")
        for user_group_xml in user_group_list_xml.findall("user_group"):
            user_group_obj = UserGroup.from_xml(ElementTree.tostring(user_group_xml), new_hallo)
            new_hallo.add_user_group(user_group_obj)
        server_list_xml = root.find("server_list")
        for server_xml in server_list_xml.findall("server"):
            server_obj = new_hallo.server_factory.new_server_from_xml(ElementTree.tostring(server_xml))
            new_hallo.add_server(server_obj)
        if root.find("permission_mask") is not None:
            new_hallo.permission_mask = PermissionMask.from_xml(ElementTree.tostring(root.find("permission_mask")))
        api_key_list_xml = root.find("api_key_list")
        for api_key_xml in api_key_list_xml.findall("api_key"):
            api_key_name = api_key_xml.findtext("name")
            api_key_key = api_key_xml.findtext("key")
            new_hallo.add_api_key(api_key_name, api_key_key)
        return new_hallo

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
        default_nick_elem.appendChild(doc.createTextNode(self.default_nick))
        root.appendChild(default_nick_elem)
        # Create default_prefix element
        if self.default_prefix is not None:
            default_prefix_elem = doc.createElement("default_prefix")
            if self.default_prefix is False:
                default_prefix_elem.appendChild(doc.createTextNode("0"))
            else:
                default_prefix_elem.appendChild(doc.createTextNode(self.default_prefix))
            root.appendChild(default_prefix_elem)
        # Create default_full_name element
        default_full_name_elem = doc.createElement("default_full_name")
        default_full_name_elem.appendChild(doc.createTextNode(self.default_full_name))
        root.appendChild(default_full_name_elem)
        # Create function dispatcher
        function_dispatcher_elem = minidom.parseString(self.function_dispatcher.to_xml()).firstChild
        root.appendChild(function_dispatcher_elem)
        # Create server list
        server_list_elem = doc.createElement("server_list")
        for server_elem in self.server_list:
            server_xml = minidom.parseString(server_elem.to_xml()).firstChild
            server_list_elem.appendChild(server_xml)
        root.appendChild(server_list_elem)
        # Create user_group list
        user_group_list_elem = doc.createElement("user_group_list")
        for user_group_name in self.user_list_list:
            user_group_elem = minidom.parseString(self.user_list_list[user_group_name].to_xml()).firstChild
            user_group_list_elem.appendChild(user_group_elem)
        root.appendChild(user_group_list_elem)
        # Create permission_mask element, if it's not empty.
        if not self.permission_mask.is_empty():
            permission_mask_elem = minidom.parseString(self.permission_mask.to_xml()).firstChild
            root.appendChild(permission_mask_elem)
        # Save api key list
        api_key_list_elem = doc.createElement("api_key_list")
        for api_key_name in self.api_key_list:
            api_key_elem = doc.createElement("api_key")
            api_key_name_elem = doc.createElement("name")
            api_key_name_elem.appendChild(doc.createTextNode(api_key_name))
            api_key_elem.appendChild(api_key_name_elem)
            api_key_key_elem = doc.createElement("key")
            api_key_key_elem.appendChild(doc.createTextNode(self.api_key_list[api_key_name]))
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
        user_group_name = user_group.get_name()
        self.user_list_list[user_group_name] = user_group

    def get_user_group_by_name(self, user_group_name):
        """
        Returns the UserGroup with the specified name
        :param user_group_name: Name of user group to search for
        :return: User Group matching specified name, or None
        """
        if user_group_name in self.user_list_list:
            return self.user_list_list[user_group_name]
        return None

    def remove_user_group_by_name(self, user_group_name):
        """
        Removes a user group specified by name
        :param user_group_name: Name of the user group to remove from list
        """
        del self.user_list_list[user_group_name]

    def add_server(self, server):
        """
        Adds a new server to the server list
        :param server: Server to add to Hallo's list of servers
        """
        self.server_list.append(server)

    def get_server_by_name(self, server_name):
        """
        Returns a server matching the given name
        :param server_name: name of the server to search for
        :return: Server matching specified name of None
        """
        for server in self.server_list:
            if server.get_name().lower() == server_name.lower():
                return server
        return None

    def get_server_list(self):
        """Returns the server list for hallo"""
        return self.server_list

    def remove_server(self, server):
        self.server_list.remove(server)

    def remove_server_by_name(self, server_name):
        for server in self.server_list:
            if server.get_name() == server_name:
                self.server_list.remove(server)

    def close(self):
        """Shuts down the entire program"""
        for server in self.server_list:
            server.disconnect()
        self.function_dispatcher.close()
        self.save_to_xml()
        self.open = False

    def rights_check(self, right_name):
        """
        Checks the value of the right with the specified name. Returns boolean
        :param right_name: name of the user right to search for
        :return: Boolean, whether or not the specified right is given
        """
        right_value = self.permission_mask.get_right(right_name)
        # If PermissionMask contains that right, return it.
        if right_value in [True, False]:
            return right_value
        # If it's a function right, go to default_function right
        if right_name.startswith("function_"):
            return self.rights_check("default_function")
        # If default_function is not defined, define and return it as True
        if right_name == "default_function":
            self.permission_mask.set_right("default_function", True)
            return True
        else:
            # Else, define and return False
            self.permission_mask.set_right(right_name, False)
            return False

    def get_default_nick(self):
        """Default nick getter"""
        return self.default_nick

    def set_default_nick(self, default_nick):
        """
        Default nick setter
        :param default_nick: The new default nick to use on all new servers
        """
        self.default_nick = default_nick

    def get_default_prefix(self):
        """Default prefix getter"""
        return self.default_prefix

    def set_default_prefix(self, default_prefix):
        """
        Default prefix setter
        :param default_prefix: Default prefix to use for commands addressed to the bot
        """
        self.default_prefix = default_prefix

    def get_default_full_name(self):
        """Default full name getter"""
        return self.default_full_name

    def set_default_full_name(self, default_full_name):
        """
        Default full name setter
        :param default_full_name: Default full name to use on all new server connections
        """
        self.default_full_name = default_full_name

    def get_permission_mask(self):
        return self.permission_mask

    def get_function_dispatcher(self):
        """Returns the FunctionDispatcher object"""
        return self.function_dispatcher

    def get_logger(self):
        """Returns the Logger object"""
        return self.logger

    def get_printer(self):
        """Returns the Printer object"""
        return self.printer

    def add_api_key(self, name, key):
        """
        Adds an api key to the list, or overwrites one.
        :param name: Name of the API to add
        :param key: The actual API key to use
        """
        self.api_key_list[name] = key

    def get_api_key(self, name):
        """
        Returns a specified api key.
        :param name: Name of the API key to retrieve
        """
        if name in self.api_key_list:
            return self.api_key_list[name]
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
    hallo = Hallo.load_from_xml()
    hallo.start()
