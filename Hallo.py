#!/usr/bin/env python3
import json
import time
import re
from datetime import datetime

from Events import EventSecond, EventMinute, EventDay, EventHour
from Server import Server
from PermissionMask import PermissionMask
from ServerFactory import ServerFactory
from ServerIRC import ServerIRC
from UserGroup import UserGroup
from FunctionDispatcher import FunctionDispatcher
from inc.Logger import Logger
from inc.Printer import Printer


class Hallo:

    def __init__(self):
        self.default_nick = "Hallo"
        """:type : str"""
        self.default_prefix = False
        """:type : bool | str"""
        self.default_full_name = "HalloBot HalloHost HalloServer :an irc bot by spangle"
        """:type : str"""
        self.open = False
        """:type : bool"""
        self.user_group_list = set()
        """:type : set[UserGroup]"""
        self.server_list = set()
        """:type : set[Server]"""
        self.logger = Logger(self)
        """:type : Logger"""
        self.printer = Printer(self)
        """:type : Printer"""
        self.api_key_list = {}
        """:type : dict[str,str]"""
        # Create ServerFactory
        self.server_factory = ServerFactory(self)
        """:type : ServerFactory"""
        self.permission_mask = PermissionMask()
        """:type : PermissionMask"""
        # TODO: manual FunctionDispatcher construction, user input?
        self.function_dispatcher = None
        """:type : FunctionDispatcher"""

    def start(self):
        # If no function dispatcher, create one
        # TODO: manual FunctionDispatcher construction, user input?
        if self.function_dispatcher is None:
            self.function_dispatcher = FunctionDispatcher({"ChannelControl", "Convert", "HalloControl", "Lookup",
                                                           "Math", "PermissionControl", "Random", "ServerControl"},
                                                          self)
        # If no servers, ask for a new server
        if len(self.server_list) == 0 or all([not server.get_auto_connect() for server in self.server_list]):
            self.manual_server_connect()
        # Connect to auto-connect servers
        self.printer.output('connecting to servers')
        for server in self.server_list:
            if server.get_auto_connect():
                server.start()
        count = 0
        while not self.connected_to_any_servers():
            time.sleep(0.1)
            count += 1
            if count > 600:
                self.open = False
                print("No servers managed to connect in 60 seconds.")
                break
        self.open = True
        # Main loop, sticks around throughout the running of the bot
        self.printer.output('connected to all servers.')
        self.core_loop_time_events()

    def connected_to_any_servers(self):
        auto_connecting_servers = [server for server in self.server_list if server.auto_connect]
        connected_list = [server.is_connected() for server in auto_connecting_servers]
        return any(connected_list)

    def core_loop_time_events(self):
        """
        Runs a loop to keep hallo running, while calling time events with the FunctionDispatcher passive dispatcher
        """
        last_date_time = datetime.now()
        while self.open:
            now_date_time = datetime.now()
            if now_date_time.second != last_date_time.second:
                second = EventSecond()
                self.function_dispatcher.dispatch_passive(second)
            if now_date_time.minute != last_date_time.minute:
                minute = EventMinute()
                self.function_dispatcher.dispatch_passive(minute)
            if now_date_time.hour != last_date_time.hour:
                hour = EventHour()
                self.function_dispatcher.dispatch_passive(hour)
            if now_date_time.day != last_date_time.day:
                day = EventDay()
                self.function_dispatcher.dispatch_passive(day)
            last_date_time = now_date_time
            time.sleep(0.1)
        self.close()

    def save_json(self):
        """
        Saves the whole hallo config to a JSON file
        :return: None
        """
        json_obj = {}
        json_obj["default_nick"] = self.default_nick
        json_obj["default_prefix"] = self.default_prefix
        json_obj["default_full_name"] = self.default_full_name
        json_obj["function_dispatcher"] = self.function_dispatcher.to_json()
        json_obj["servers"] = []
        for server in self.server_list:
            json_obj["servers"].append(server.to_json())
        json_obj["user_groups"] = []
        for user_group in self.user_group_list:
            json_obj["user_groups"].append(user_group.to_json())
        if not self.permission_mask.is_empty():
            json_obj["permission_mask"] = self.permission_mask.to_json()
        json_obj["api_keys"] = {}
        for api_key_name in self.api_key_list:
            json_obj["api_keys"][api_key_name] = self.api_key_list[api_key_name]
        # Write json to file
        with open("config/config.json", "w+") as f:
            json.dump(json_obj, f, indent=2)

    @staticmethod
    def load_json():
        """
        Loads up the json configuration and creates a new Hallo object
        :return: new Hallo object
        :rtype: Hallo
        """
        try:
            with open("config/config.json", "r") as f:
                json_obj = json.load(f)
        except (OSError, IOError):
            print("No current config, loading from default.")
            with open("config/config-default.json", "r") as f:
                json_obj = json.load(f)
        # Create new hallo object
        new_hallo = Hallo()
        new_hallo.default_nick = json_obj["default_nick"]
        new_hallo.default_prefix = json_obj["default_prefix"]
        new_hallo.default_full_name = json_obj["default_full_name"]
        new_hallo.function_dispatcher = FunctionDispatcher.from_json(json_obj["function_dispatcher"], new_hallo)
        # User groups must be done before servers, as users will try and look up and add user groups!
        for user_group in json_obj["user_groups"]:
            new_hallo.add_user_group(UserGroup.from_json(user_group, new_hallo))
        for server in json_obj["servers"]:
            new_server = new_hallo.server_factory.new_server_from_json(server)
            new_hallo.add_server(new_server)
        if "permission_mask" in json_obj:
            new_hallo.permission_mask = PermissionMask.from_json(json_obj["permission_mask"])
        for api_key in json_obj["api_keys"]:
            new_hallo.add_api_key(api_key, json_obj["api_keys"][api_key])
        return new_hallo

    def add_user_group(self, user_group):
        """
        Adds a new UserGroup to the UserGroup list
        :param user_group: UserGroup to add to the hallo object's list of user groups
        :type user_group: UserGroup
        """
        self.user_group_list.add(user_group)

    def get_user_group_by_name(self, user_group_name):
        """
        Returns the UserGroup with the specified name
        :param user_group_name: Name of user group to search for
        :type user_group_name: str
        :return: User Group matching specified name, or None
        :rtype: UserGroup | None
        """
        for user_group in self.user_group_list:
            if user_group_name == user_group.name:
                return user_group
        return None

    def remove_user_group(self, user_group):
        """
        Removes a user group specified by name
        :param user_group: Name of the user group to remove from list
        :type user_group: UserGroup
        """
        self.user_group_list.remove(user_group)

    def add_server(self, server):
        """
        Adds a new server to the server list
        :param server: Server to add to Hallo's list of servers
        :type server: Server.Server
        """
        self.server_list.add(server)

    def get_server_by_name(self, server_name):
        """
        Returns a server matching the given name
        :param server_name: name of the server to search for
        :type server_name: str
        :return: Server matching specified name of None
        :rtype: Server | None
        """
        for server in self.server_list:
            if server.name.lower() == server_name.lower():
                return server
        return None

    def remove_server(self, server):
        """
        Removes a server from the list of servers
        :param server: The server to remove
        :type server: Server.Server
        """
        self.server_list.remove(server)

    def remove_server_by_name(self, server_name):
        """
        Removes a server, specified by name, from the list of servers
        :param server_name: Name of the server to remove
        :type server_name: str
        """
        for server in self.server_list:
            if server.name.lower() == server_name.lower():
                self.server_list.remove(server)

    def close(self):
        """Shuts down the entire program"""
        for server in self.server_list:
            if server.state != Server.STATE_CLOSED:
                server.disconnect()
        self.function_dispatcher.close()
        self.save_json()
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

    def add_api_key(self, name, key):
        """
        Adds an api key to the list, or overwrites one.
        :param name: Name of the API to add
        :type name: str
        :param key: The actual API key to use
        :type key: str
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
        server_match = re.match(r'([a-z\d.-]+\.)?([a-z\d-]{1,63})\.([a-z]{2,3}\.[a-z]{2}|[a-z]{2,6})', server_url,
                                re.I)
        server_name = server_match.group(2)
        # Create the server object
        new_server = ServerIRC(self, server_name, server_url, server_port)
        # Add new server to server list
        self.add_server(new_server)
        # Save XML
        self.save_json()
        print("Config file saved.")


if __name__ == '__main__':
    hallo = Hallo.load_json()
    hallo.start()
