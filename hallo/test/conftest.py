import asyncio

import pytest

from hallo.function_dispatcher import FunctionDispatcher
from hallo.hallo import Hallo
from hallo.test.server_mock import ServerMock

DEFAULT_MODULES = {
    "ascii_art",
    "bio",
    "channel_control",
    "convert",
    "euler",
    "hallo_control",
    "math",
    "permission_control",
    "random",
    "server_control",
    "silly",
    "subscriptions",
}


class TestHallo(Hallo):
    def __init__(self):
        super().__init__()
        # Create server
        self.test_server = ServerMock(self)
        self.test_server.name = "mock-server"
        self.add_server(self.test_server)
        # Test user and channel
        self._test_user = None
        self._test_chan = None
        self._hallo_user = None

    def set_modules(self, modules: set[str] | None) -> None:
        modules = modules or DEFAULT_MODULES
        self.function_dispatcher = FunctionDispatcher(modules, self)

    def _init_test_destinations(self):
        self._hallo_user = self.test_server.get_user_by_address(
            self.test_server.get_nick().lower(), self.test_server.get_nick()
        )
        self._test_user = self.test_server.get_user_by_address("test", "test")
        self._test_user.online = True
        self._test_chan = self.test_server.get_channel_by_address("#test", "#test")
        self._test_chan.in_channel = True
        self._test_chan.add_user(self._hallo_user)
        self._test_chan.add_user(self._test_user)

    @property
    def hallo_user(self):
        if self._hallo_user is None:
            self._init_test_destinations()
        return self._hallo_user

    @property
    def test_user(self):
        if self._test_user is None:
            self._init_test_destinations()
        return self._test_user

    @property
    def test_chan(self):
        if self._test_chan is None:
            self._init_test_destinations()
        return self._test_chan


@pytest.fixture
async def hallo_getter():
    # Create a Hallo
    hallo = TestHallo()

    async def function(modules: set[str] | None = None, disconnect_servers: bool = False):
        hallo.set_modules(modules)
        # Start hallo thread
        hallo.start_task()
        # Wait until hallo is open
        count = 0
        while not hallo.open:
            await asyncio.sleep(0.01)
            count += 1
            assert count < 1000, "Hallo took too long to start."
            if count > 1000:
                break
        # Clear any data in the server
        hallo.test_server.get_send_data()
        # Disconnect servers if wanted
        if disconnect_servers:
            for server in hallo.server_list:
                await server.disconnect(True)
            hallo.server_list.clear()
        return hallo

    yield function
    await hallo.close()
    asyncio.get_event_loop().run_until_complete(hallo.end_task())
