import isodate
import pytest

from hallo.events import EventMessage
from hallo.hallo import Hallo
from hallo.modules.subscriptions.source_e621 import E621Source
from hallo.modules.subscriptions.subscription_repo import SubscriptionRepo
from hallo.test.server_mock import ServerMock


def test_init():
    rf = E621Source("cabinet")
    keys = [
        "search",
        "last_keys"
    ]
    for key in keys:
        assert key in rf.__dict__, "Key is missing from E621Sub object: " + key


@pytest.mark.external_integration
def test_check_search(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"subscriptions"})
    # Check loading up an example search
    test_search = "cabinet"
    rf = E621Source(test_search)
    new_items = rf.check()
    assert len(new_items) == 50
    for new_item in new_items:
        format_item = rf.format_item(new_item).text
        assert (
                "(Explicit)" in format_item
                or "(Questionable)" in format_item
                or "(Safe)" in format_item
        ), ("Rating not in formatted item: " + format_item)
        assert "e621.net/posts/", "E621 link not in formatted item: " + format_item
    # Check that calling twice returns no more items
    next_items = rf.check()
    assert len(next_items) == 0, "More items should not have been found. Found " + str(
        len(next_items)
    )


def test_format_item(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"subscriptions"})
    item_id = "572912"
    item_rating = "q"
    rf = E621Source("cabinet")
    json_data = dict()
    json_data["id"] = item_id
    json_data["rating"] = item_rating
    json_data["file"] = {}
    json_data["file"]["url"] = "http://spangle.org.uk/haskell.jpg"
    json_data["file"]["ext"] = "jpg"
    # Get output and check it
    output = rf.item_to_event(test_server, None, None, json_data).text
    assert item_id in output
    assert "(Questionable)" in output


def test_output_item(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"subscriptions"})
    # Create example e621 sub element
    item_id = "652362"
    item_rate = "q"
    item_rating = "(Questionable)"
    item_elem = {
        "id": item_id,
        "rating": item_rate,
        "file": {
            "url": "12345",
            "ext": "png"
        }
    }
    # Check output works with given server and channel
    rf1 = E621Source("cabinet")
    rf1.update_frequency = isodate.parse_duration("P1D")
    rf1.send_item(item_elem)
    data = test_server.get_send_data(1, test_channel, EventMessage)
    assert item_id in data[0].text
    assert item_rating in data[0].text
    # Check output works with given server not channel
    serv2 = ServerMock(hallo)
    serv2.name = "test_serv2"
    hallo.add_server(serv2)
    chan2 = serv2.get_channel_by_address("test_chan2".lower(), "test_chan2")
    rf2 = E621Source("clefable")
    rf2.send_item(item_elem)
    data = serv2.get_send_data(1, chan2, EventMessage)
    assert item_id in data[0].text
    assert item_rating in data[0].text
    # Check output works with given server not user
    serv3 = ServerMock(hallo)
    serv3.name = "test_serv3"
    hallo.add_server(serv3)
    user3 = serv3.get_user_by_address("test_user3".lower(), "test_user3")
    rf3 = E621Source("fez")
    rf3.send_item(item_elem)
    data = serv3.get_send_data(1, user3, EventMessage)
    assert item_id in data[0].text
    assert item_rating in data[0].text
    # Check output works without given server with given channel
    hallo4 = Hallo()
    serv4 = ServerMock(hallo4)
    serv4.name = "test_serv4"
    hallo4.add_server(serv4)
    chan4 = serv4.get_channel_by_address("test_chan4".lower(), "test_chan4")
    rf4 = E621Source("cabinet")
    rf4.send_item(item_elem)
    data = serv4.get_send_data(1, chan4, EventMessage)
    assert item_id in data[0].text
    assert item_rating in data[0].text
    # Check output works without given server with given user
    hallo5 = Hallo()
    serv5 = ServerMock(hallo5)
    serv5.name = "test_serv5"
    hallo5.add_server(serv5)
    chan5 = serv5.get_channel_by_address("test_chan5".lower(), "test_chan5")
    rf5 = E621Source("clefable")
    rf5.send_item(item_elem)
    data = serv5.get_send_data(1, chan5, EventMessage)
    assert item_id in data[0].text
    assert item_rating in data[0].text
    # Check output works without given server or channel to channel
    hallo6 = Hallo()
    serv6 = ServerMock(hallo6)
    serv6.name = "test_serv6"
    hallo6.add_server(serv6)
    chan6 = serv6.get_channel_by_address("test_chan6".lower(), "test_chan6")
    rf6 = E621Source("fez")
    rf6.server_name = "test_serv6"
    rf6.channel_address = "test_chan6"
    rf6.send_item(item_elem)
    data = serv6.get_send_data(1, chan6, EventMessage)
    assert item_id in data[0].text
    assert item_rating in data[0].text
    # Check output works without given server or channel to user
    hallo7 = Hallo()
    serv7 = ServerMock(hallo7)
    serv7.name = "test_serv7"
    hallo7.add_server(serv7)
    user7 = serv7.get_user_by_address("test_user7".lower(), "test_user7")
    rf7 = E621Source("clefable")
    rf7.send_item(item_elem)
    data = serv7.get_send_data(1, user7, EventMessage)
    assert item_id in data[0].text
    assert item_rating in data[0].text


@pytest.mark.external_integration
def test_json(hallo_getter):
    hallo, test_server, test_channel, test_user = hallo_getter({"subscriptions"})
    test_e621_search = "cabinet"
    test_seconds = 3600
    test_days = 0
    # Create example feed
    sub_repo = SubscriptionRepo()
    rf = E621Source(test_e621_search)
    # Clear off the current items
    rf.check()
    # Ensure there are no new items
    new_items = rf.check()
    assert len(new_items) == 0
    # Save to json and load up new E621Sub
    rf_json = rf.to_json()
    rf2 = E621Source.from_json(rf_json, test_channel, sub_repo)
    # Ensure there's still no new items
    new_items = rf2.check()
    assert len(new_items) == 0
    assert rf2.update_frequency.days == test_days
    assert rf2.update_frequency.seconds == test_seconds
