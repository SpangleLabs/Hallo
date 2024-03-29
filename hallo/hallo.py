#!/usr/bin/env python3
import json
import logging
import re
import time
from datetime import datetime
from typing import Union, Set, Dict, Optional

import heartbeat
from prometheus_client import start_http_server
from prometheus_client.metrics import Gauge

from hallo.errors import MessageError
from hallo.events import EventSecond, EventMinute, EventDay, EventHour
from hallo.function_dispatcher import FunctionDispatcher
from hallo.permission_mask import PermissionMask
from hallo.server import Server
from hallo.server_factory import ServerFactory
from hallo.server_irc import ServerIRC
from hallo.user_group import UserGroup

heartbeat.heartbeat_app_url = "https://heartbeat.spangle.org.uk/"
heartbeat_app_name = "Hallo"

logger = logging.getLogger(__name__)
usage_logger = logging.getLogger("usage")


start_time = Gauge(
    "hallo_start_unixtime",
    "Unix timestamp of the last time the bot started up"
)
server_count = Gauge(
    "hallo_server_count",
    "Number of servers hallo knows about"
)
server_connected_count = Gauge(
    "hallo_server_connected_count",
    "Number of servers hallo is connected to"
)


class Hallo:
    CONFIG_FILE = "config/config.json"
    CONFIG_DEFAULT_FILE = "config/config-default.json"

    def __init__(self):
        self.default_nick: str = "Hallo"
        self.default_prefix: Union[bool, str] = False
        self.default_full_name: str = "HalloBot HalloHost HalloServer :an irc bot by spangle"
        self.open: bool = False
        self.user_group_list: Set[UserGroup] = set()
        self.server_list: Set[Server] = set()
        self.api_key_list: Dict[str, str] = {}
        self.server_factory: ServerFactory = ServerFactory(self)
        self.permission_mask: PermissionMask = PermissionMask()
        self.prom_port = 7265
        server_count.set_function(lambda: len(self.server_list))
        server_connected_count.set_function(lambda: len([s for s in self.server_list.copy() if s.is_connected()]))
        # TODO: manual FunctionDispatcher construction, user input?
        self.function_dispatcher: FunctionDispatcher = None

    def start(self) -> None:
        # If no function dispatcher, create one
        # TODO: manual FunctionDispatcher construction, user input?
        if self.function_dispatcher is None:
            self.function_dispatcher = FunctionDispatcher(
                {
                    "channel_control",
                    "convert",
                    "hallo_control",
                    "lookup",
                    "math",
                    "permission_control",
                    "random",
                    "server_control",
                },
                self,
            )
        # If no servers, ask for a new server
        if len(self.server_list) == 0 or all(
                [not server.get_auto_connect() for server in self.server_list]
        ):
            self.manual_server_connect()
        # Connect to auto-connect servers
        logger.info("Connecting to servers")
        for server in self.server_list:
            if server.get_auto_connect():
                server.start()
        count = 0
        while not self.connected_to_any_servers():
            time.sleep(0.01)
            count += 1
            if count > 6000:
                self.open = False
                error = MessageError("No servers managed to connect in 60 seconds.")
                logger.error(error.get_log_line())
                return
        self.open = True
        # Start up prometheus server
        start_http_server(self.prom_port)
        start_time.set_to_current_time()
        # Main loop, sticks around throughout the running of the bot
        logger.info("Connected to all servers.")
        self.core_loop_time_events()

    def connected_to_any_servers(self) -> bool:
        auto_connecting_servers = [
            server for server in self.server_list if server.auto_connect
        ]
        connected_list = [server.is_connected() for server in auto_connecting_servers]
        return any(connected_list)

    def core_loop_time_events(self) -> None:
        """
        Runs a loop to keep hallo running, while calling time events with the FunctionDispatcher passive dispatcher
        """
        last_date_time = datetime.now()
        while self.open:
            now_date_time = datetime.now()
            try:
                if now_date_time.second != last_date_time.second:
                    second = EventSecond()
                    self.function_dispatcher.dispatch_passive(second)
                if now_date_time.minute != last_date_time.minute:
                    logger.debug("Core heartbeat")
                    heartbeat.update_heartbeat(heartbeat_app_name)
                    minute = EventMinute()
                    self.function_dispatcher.dispatch_passive(minute)
                if now_date_time.hour != last_date_time.hour:
                    hour = EventHour()
                    self.function_dispatcher.dispatch_passive(hour)
                if now_date_time.day != last_date_time.day:
                    day = EventDay()
                    self.function_dispatcher.dispatch_passive(day)
            except Exception as e:
                logger.error("Error sending core time loop event.", exc_info=e)
            last_date_time = now_date_time
            time.sleep(0.1)
        self.close()

    def save_json(self) -> None:
        """
        Saves the whole hallo config to a JSON file
        :return: None
        """
        json_obj = dict()
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
        with open(self.CONFIG_FILE, "w+") as f:
            json.dump(json_obj, f, indent=2)

    @classmethod
    def load_json(cls) -> 'Hallo':
        """
        Loads up the json configuration and creates a new Hallo object
        :return: new Hallo object
        :rtype: Hallo
        """
        try:
            with open(cls.CONFIG_FILE, "r") as f:
                json_obj = json.load(f)
        except (OSError, IOError):
            error = MessageError("No current config, loading from default.")
            logger.error(error.get_log_line())
            with open(cls.CONFIG_DEFAULT_FILE, "r") as f:
                json_obj = json.load(f)
        # Create new hallo object
        new_hallo = cls()
        new_hallo.default_nick = json_obj["default_nick"]
        new_hallo.default_prefix = json_obj["default_prefix"]
        new_hallo.default_full_name = json_obj["default_full_name"]
        new_hallo.function_dispatcher = FunctionDispatcher.from_json(
            json_obj["function_dispatcher"], new_hallo
        )
        # User groups must be done before servers, as users will try and look up and add user groups!
        for user_group in json_obj["user_groups"]:
            new_hallo.add_user_group(UserGroup.from_json(user_group, new_hallo))
        for server in json_obj["servers"]:
            new_server = new_hallo.server_factory.new_server_from_json(server)
            new_hallo.add_server(new_server)
        if "permission_mask" in json_obj:
            new_hallo.permission_mask = PermissionMask.from_json(
                json_obj["permission_mask"]
            )
        for api_key in json_obj["api_keys"]:
            new_hallo.add_api_key(api_key, json_obj["api_keys"][api_key])
        return new_hallo

    def add_user_group(self, user_group: UserGroup) -> None:
        """
        Adds a new UserGroup to the UserGroup list
        :param user_group: UserGroup to add to the hallo object's list of user groups
        """
        self.user_group_list.add(user_group)

    def get_user_group_by_name(self, user_group_name: str) -> Optional[UserGroup]:
        """
        Returns the UserGroup with the specified name
        :param user_group_name: Name of user group to search for
        :return: User Group matching specified name, or None
        """
        for user_group in self.user_group_list:
            if user_group_name == user_group.name:
                return user_group
        return None

    def remove_user_group(self, user_group: UserGroup) -> None:
        """
        Removes a user group specified by name
        :param user_group: Name of the user group to remove from list
        :type user_group: UserGroup
        """
        self.user_group_list.remove(user_group)

    def add_server(self, server: Server) -> None:
        """
        Adds a new server to the server list
        :param server: Server to add to Hallo's list of servers
        :type server: Server.Server
        """
        self.server_list.add(server)

    def get_server_by_name(self, server_name: str) -> Optional[Server]:
        """
        Returns a server matching the given name
        :param server_name: name of the server to search for
        :return: Server matching specified name of None
        """
        for server in self.server_list:
            if server.name.lower() == server_name.lower():
                return server
        return None

    def remove_server(self, server: Server) -> None:
        """
        Removes a server from the list of servers
        :param server: The server to remove
        :type server: Server.Server
        """
        self.server_list.remove(server)

    def remove_server_by_name(self, server_name: str) -> None:
        """
        Removes a server, specified by name, from the list of servers
        :param server_name: Name of the server to remove
        """
        for server in self.server_list:
            if server.name.lower() == server_name.lower():
                self.server_list.remove(server)

    def close(self) -> None:
        """Shuts down the entire program"""
        for server in self.server_list:
            if server.state != Server.STATE_CLOSED:
                server.disconnect()
        self.function_dispatcher.close()
        self.save_json()
        self.open = False

    def rights_check(self, right_name: str) -> bool:
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

    def add_api_key(self, name: str, key: str) -> None:
        """
        Adds an api key to the list, or overwrites one.
        :param name: Name of the API to add
        :type name: str
        :param key: The actual API key to use
        :type key: str
        """
        self.api_key_list[name] = key

    def get_api_key(self, name: str) -> Optional[str]:
        """
        Returns a specified api key.
        :param name: Name of the API key to retrieve
        """
        if name in self.api_key_list:
            return self.api_key_list[name]
        return None

    def manual_server_connect(self) -> None:
        # TODO: add ability to connect to non-IRC servers
        logger.error(
            "No servers have been loaded or connected to. Please connect to an IRC server."
        )
        # godNick = input("What nickname is the bot operator using? [deer-spangle] ")
        # godNick = godNick.replace(' ', '')
        # if godNick == '':
        #     godNick = 'deer-spangle'
        # TODO: do something with godNick
        server_addr = input(
            "What server should the bot connect to? [irc.freenode.net:6667] "
        )
        server_addr = server_addr.replace(" ", "")
        if server_addr == "":
            server_addr = "irc.freenode.net:6667"
        server_url = server_addr.split(":")[0]
        server_port = int(server_addr.split(":")[1])
        server_match = re.match(
            r"([a-z\d.-]+\.)?([a-z\d-]{1,63})\.([a-z]{2,3}\.[a-z]{2}|[a-z]{2,6})",
            server_url,
            re.I,
        )
        server_name = server_match.group(2)
        # Create the server object
        new_server = ServerIRC(self, server_name, server_url, server_port)
        # Add new server to server list
        self.add_server(new_server)
        # Save XML
        self.save_json()
        logger.info("Config file saved.")


if __name__ == "__main__":
    hallo = Hallo.load_json()
    hallo.start()
