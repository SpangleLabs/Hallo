from hallo.events import EventMessage
from hallo.modules.random.night_vale_proverb import NightValeProverb


def test_proverb(mock_chooser, hallo_getter):
    test_hallo = hallo_getter({"random"})
    # Get proverb list
    n = NightValeProverb()
    proverb_list = n.proverb_list
    response_list = []
    # Check all proverbs are given
    for x in range(len(proverb_list)):
        # Set RNG
        mock_chooser.choice = x
        # Check function
        test_hallo.function_dispatcher.dispatch(
            EventMessage(test_hallo.test_server, None, test_hallo.test_user, "nightvale proverb")
        )
        data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
        assert data[0].text in proverb_list, "Proverb isn't from list"
        response_list.append(data[0].text)
    assert len(response_list) == len(
        proverb_list
    ), "Not all proverbs options given?"
    assert set(response_list) == set(proverb_list), "Proverb options didn't match"
