from contextlib import contextmanager
from unittest.mock import Mock

from hallo.events import EventMessage
from hallo.test.conftest import TestHallo
from hallo.test.modules.convert.mock_repo import mock_repo


@contextmanager
def mock_convert_parse(test_hallo: TestHallo):
    output_parse = "{parse called}"
    mock_parse = Mock(return_value=output_parse)
    conv_class = test_hallo.function_dispatcher.get_function_by_name("convert")
    conv_obj = test_hallo.function_dispatcher.get_function_object(conv_class)
    conv_parse = conv_obj.convert_parse
    conv_obj.convert_parse = mock_parse
    try:
        yield mock_parse
    finally:
        conv_obj.convert_parse = conv_parse


def test_passive_run(tmp_path, hallo_getter):
    test_hallo = hallo_getter({"convert"})
    mock_repo(tmp_path, test_hallo)
    with mock_convert_parse(test_hallo) as mock_parse:
        test_hallo.function_dispatcher.dispatch_passive(
            EventMessage(
                test_hallo.test_server, test_hallo.test_chan, test_hallo.test_user, "1 unit1b to unit1a"
            )
        )
        data = test_hallo.test_server.get_send_data(1, test_hallo.test_chan, EventMessage)
        mock_parse.assert_called_once()
        assert data[0].text == mock_parse.return_value
        assert mock_parse.call_args[0] == ("1 unit1b to unit1a", True)


def test_run(hallo_getter):
    test_hallo = hallo_getter({"convert"})
    with mock_convert_parse(test_hallo) as mock_parse:
        test_hallo.function_dispatcher.dispatch(
            EventMessage(
                test_hallo.test_server, None, test_hallo.test_user, "convert 1 unit1b to unit1a"
            )
        )
        data = test_hallo.test_server.get_send_data(1, test_hallo.test_user, EventMessage)
        assert data[0].text == mock_parse.return_value
        assert mock_parse.call_args[0] == ("1 unit1b to unit1a",)


def test_load_repo(hallo_getter):
    test_hallo = hallo_getter({"convert"})
    conv_cls = test_hallo.function_dispatcher.get_function_by_name("convert")
    conv_obj = test_hallo.function_dispatcher.get_function_object(conv_cls)
    assert conv_obj.convert_repo is not None
    assert conv_obj.convert_repo.__class__.__name__ == "ConvertRepo"
    assert len(conv_obj.convert_repo.type_list) > 0
