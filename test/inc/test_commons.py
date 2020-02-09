import re

from datetime import timedelta, datetime

import pytest

from inc.commons import Commons, ISO8601ParseError


@pytest.mark.parametrize(
    "calculation",
    [
        "23",
        "2.123",
        "cos(12.2)",
        "tan(sin(atan(cosh(1))))",
        "pie",
        "1+2*3/4^5%6",
        "gamma(17)",
    ],
)
def test_check_calculation__valid(calculation):
    assert Commons.check_calculation(calculation), (
        "Valid string judged to be not calculation, " + calculation
    )


@pytest.mark.parametrize(
    "calculation", ["hello", "1&2", "$13.50", "1::", "cos(tan(12+t+15))"]
)
def test_check_calculation__invalid(calculation):
    assert not Commons.check_calculation(calculation), (
        "Invalid string judged to be calculation, " + calculation
    )


@pytest.mark.parametrize("calculation", ["23", "2.123", " 97", "9 7"])
def test_check_numbers__valid(calculation):
    assert Commons.check_numbers(calculation), (
        "Valid string judged to be not calculation, " + calculation
    )


@pytest.mark.parametrize(
    "calculation",
    [
        "127.0.0.1",
        "cos(12.2)",
        "tan(sin(atan(cosh(1))))",
        "pie",
        "1+2*3/4^5%6",
        "gamma(17)",
        "hello",
        "1&2",
        "$13.50",
        "1::",
        "cos(tan(12+t+15))",
    ],
)
def test_check_numbers__invalid(calculation):
    assert not Commons.check_numbers(calculation), (
        "Invalid string judged to be calculation, " + calculation
    )


def test_chunk_string_dot__under_limit():
    string1 = "a" * 50
    chunks1 = Commons.chunk_string_dot(string1, 100)
    assert len(chunks1) == 1, "Should only be one chunk when splitting " + string1
    assert chunks1[0] == string1, "Should not have changed string " + string1


def test_chunk_string_dot__on_limit():
    string2 = "a" * 100
    chunks2 = Commons.chunk_string_dot(string2, 100)
    assert len(chunks2) == 1, "Should only be one chunk when splitting " + string2
    assert chunks2[0] == string2, "Should not have changed string " + string2


def test_chunk_string_dot__just_over_limit():
    string3 = "a" * 101
    chunks3 = Commons.chunk_string_dot(string3, 100)
    assert len(chunks3) == 2, "Should have split string into 2 chunks: " + string3
    assert len(chunks3[0]) == 100, (
        "First chunk should be exactly 100 characters " + chunks3[0]
    )
    assert (
        chunks3[0] == "a" * 97 + "..."
    ), "First chunk of string was not created correctly"
    assert chunks3[1] == "..." + "a" * (
        101 - 97
    ), "Second chunk of string was not created correctly."


def test_chunk_string_dot__just_under_double_limit():
    string4 = "a" * 97 * 2
    chunks4 = Commons.chunk_string_dot(string4, 100)
    assert len(chunks4) == 2, "Should have split string into just 2 chunks."
    assert len(chunks4[0]) == 100, "First chunk should be exactly 100 characters"
    assert len(chunks4[1]) == 100, "Second chunk should be exactly 100 characters"
    assert (
        chunks4[0] == "a" * 97 + "..."
    ), "First chunk of string was not created correctly"
    assert (
        chunks4[1] == "..." + "a" * 97
    ), "Second chunk of string was not created correctly."


def test_chunk_string_dot__just_under_triple_limit():
    string5 = "a" * (97 * 3 - 3)
    chunks5 = Commons.chunk_string_dot(string5, 100)
    assert len(chunks5) == 3, "Should have split string into 3 chunks"
    assert len(chunks5[0]) == 100, "First chunk should be 100 characters"
    assert len(chunks5[1]) == 100, "Second chunk should be 100 characters"
    assert len(chunks5[2]) == 100, "Third chunk should be 100 characters"
    assert chunks5[0] == "a" * 97 + "...", "First chunk created incorrectly."
    assert chunks5[1] == "..." + "a" * 94 + "...", "Second chunk created incorrectly."
    assert chunks5[2] == "..." + "a" * 97, "Third chunk created incorrectly."


def test_chunk_string_dot__just_over_triple_limit():
    string6 = "a" * (97 * 3 - 2)
    chunks6 = Commons.chunk_string_dot(string6, 100)
    assert len(chunks6) == 4, "Should have split string into 4 chunks"
    assert len(chunks6[0]) == 100, "First chunk should be 100 characters"
    assert len(chunks6[1]) == 100, "Second chunk should be 100 characters"
    assert len(chunks6[2]) == 100, "Third chunk should be 100 characters"
    assert chunks6[0] == "a" * 97 + "...", "First chunk created incorrectly"
    assert chunks6[1] == "..." + "a" * 94 + "...", "Second chunk created incorrectly"
    assert chunks6[2] == "..." + "a" * 94 + "...", "Third chunk created incorrectly"
    assert chunks6[3] == "..." + "a" * (
        (97 * 3 - 2) - (94 + 94 + 97)
    ), "Forth chunk created incorrectly"


def test_current_timestamp():
    stamp = Commons.current_timestamp()
    assert len(stamp) == 10, "Timestamp is the wrong length"
    pattern = re.compile(r"^\[(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]\]$")
    assert pattern.match(stamp), "Timestamp is not valid to defined format."


def test_current_timestamp__datetime_given():
    dtime = datetime(2019, 4, 6, 10, 15, 3)
    stamp = Commons.current_timestamp(dtime)
    assert stamp == "[10:15:03]"


@pytest.mark.parametrize(
    "delta, iso",
    [
        (timedelta(5, 5), "P5T5S"),
        (timedelta(0, 50), "P0T50S"),
        (timedelta(3, 0, 0, 0, 1), "P3T60S"),
        (timedelta(2, 0, 0, 0, 0, 1), "P2T3600S"),
        (timedelta(0, 0, 0, 0, 0, 0, 1), "P7T0S"),
    ],
)
def test_format_time_delta(delta, iso):
    assert Commons.format_time_delta(delta) == iso


@pytest.mark.parametrize(
    "unix, iso",
    [
        (0, "1970-01-01 00:00:00"),
        (1000000000, "2001-09-09 01:46:40"),
        (1234567890, "2009-02-13 23:31:30"),
    ],
)
def test_format_unix_time(unix, iso):
    assert Commons.format_unix_time(unix) == iso


@pytest.mark.parametrize(
    "string, calc",
    [
        ("$12*17", "12*17"),
        ("cos(tan(12+t+15))", "cos(tan(12+"),
        ("hello", None),
        ("£13.50", "13.50"),
        ("23f234", "23"),  # Should prioritise getting calc at start
        ("tasty pie", " pie"),  # Bit odd, but should work
    ],
)
def test_get_calc_from_start_or_end(string, calc):
    assert Commons.get_calc_from_start_or_end(string) == calc


@pytest.mark.parametrize(
    "string, digits",
    [
        ("$12*17", "17"),
        ("cos(tan(12+t+15))", None),
        ("hello", None),
        ("£13.50", "13.50"),
        ("23f234", "23"),  # Should prioritise getting calc at start
        ("tasty pie", None),
        ("2e7c", "2e7"),  # Should work with e notation
    ],
)
def test_get_digits_from_start_or_end(string, digits):
    assert Commons.get_digits_from_start_or_end(string) == digits


@pytest.mark.parametrize(
    "url, domain",
    [
        ("https://github.com/joshcoales", "github"),
        ("http://spangle.org.uk/things/stuff/hallo.html.com", "spangle"),
        ("irc://irc.freenode.net:6666", "freenode"),
        (
            "http://www.longurlmaker.com/go?id=143GetShortyShrtndspread%2Bout1tprotractedlongishYepItlofty1stre"
            "tch100RedirxMyURL1Sitelutionsspread%2Bout56706Ne1kfar%2Breachingstretchenlarged8U76SimURL01URLvi00"
            "distantr1towering46URLcutNe14m3q5stringy0elongatedremote7RubyURLRubyURL0300lasting52ny54blnk.inRed"
            "irx0t0akstretchedst765330DigBigf14922f8014v03121qeURl.ied99FhURL1MyURLFhURL8sustainedlingeringrunn"
            "ing07bYATUC68yU7618farawaystretchedxlfarawaySHurlcU760stretched01drangyccmstretchkrunningrremote52"
            "ganglingMyURL81outstretchedTraceURL5aenduring60Is.gd5stretch69660Miniliengangling112vYATUC01drawn%"
            "2Bout29extensive1URLcutc03ShredURLfspread%2Boutoutstretched1EzURLTinyURLhigh0301URL7WapURL0u7Redir"
            "x5229NutshellURLdrawn%2Boutwcfy68rangy4longish4SitelutionsG8LFwdURLe1stretchNanoRef56running2Start"
            "URLspun%2BoutShortURL165MooURL4bTightURL00URLPieprolongedWapURLw0TightURL61runningdistantShorl8951"
            "hw2MooURLelongatek8lofty1TinyURLc1qMetamark920bgelongate19n103c1dTinyLinkcontinuedlnk.in96591Decen"
            "tURL0afar%2Breaching81elongish504zremotec0l0e0adistants11high04DecentURL2stretchYATUCSnipURLstring"
            "ys7b8deepTightURL1PiURLpa7elongatedix0101Shim0Is.gdfar%2BreachingB65f8ctoweringNutshellURLWapURL1v"
            "9runningRubyURLURl.ie0ganglingEasyURL1ShortURL161stringy0h8extensivePiURL14prolongedEzURLt710dista"
            "nt1100rNanoRefh5311450ShrinkURLFwdURL1mstretched119ganglingURLCuttera11fFhURL1b6tallFwdURLdlengthy"
            "110spun%2Bout7lastingf49Fly29loftyf5jXil0spread%2Bout4lengthyrangystretch8up0URL.co.uklingeringegU"
            "RLHawk48zlengthyb3prolonged58loftyg18drawn%2BoutURLCutterURLHawk01cShortlinkshigh4remote1StartURLp"
            "rolongedURLHawk0z03Shortlinks54gURLvi18elongatedEasyURL18elongated04WapURL1lofty51spread%2Bout1Red"
            "irx1A2N5411zfar%2Breachingf001prolonged01a4dstretchsustainedoutstretchedShortURL612TraceURLURLvi00"
            "lasting28ec1URLcutcstringy827klengthyk1141DigBig9fcSHurl1Beam.toShorl0tstretchxURLCutterYepItnblas"
            "ting080stretched1FhURL15rangy1x6600continuedShredURLblnk.inelongated00413outstretched0090146stretc"
            "hed589z05stringyc8sdielongatelongish6kprolongedfar%2Breachingf36ubaTinyURL1TinyLink341028017EasyUR"
            "Ld1runningfar%2Breaching06stretching1U76spun%2Bout1cstretch",
            "longurlmaker",
        ),
        ("http://domains.ninja", "domains"),
    ],
)
def test_domain_name(url, domain):
    assert Commons.get_domain_name(url) == domain


def test_get_random_choice():
    for count in range(1, 3):
        for max_int in range(2, 10):
            for min_int in range(1, 5):
                if min_int > max_int:
                    continue
                input_list = list(range(min_int, max_int + 1))
                rand_list = Commons.get_random_choice(input_list, count)
                assert len(rand_list) == count, (
                    "Random choice list is the wrong length. "
                    + str(rand_list)
                    + " not "
                    + str(count)
                    + " elements"
                )
                for rand in rand_list:
                    assert rand in input_list


def test_get_random_int():
    for count in range(1, 3):
        for max_int in range(2, 10):
            for min_int in range(1, 5):
                if min_int > max_int:
                    continue
                rand_list = Commons.get_random_int(min_int, max_int, count)
                assert len(rand_list) == count, (
                    "Random integer list is the wrong length. "
                    + str(rand_list)
                    + " not "
                    + str(count)
                    + " elements"
                )
                for rand in rand_list:
                    assert rand >= min_int, (
                        "Random integer was too small. "
                        + str(rand)
                        + " < "
                        + str(min_int)
                    )
                    assert rand <= max_int, (
                        "Random integer was too big. "
                        + str(rand)
                        + " > "
                        + str(max_int)
                    )


@pytest.mark.parametrize("calculation", ["23", "2.123", " 97"])
def test_is_float_string__valid(calculation):
    assert Commons.is_float_string(calculation), (
        "Valid string judged to be not float, " + calculation
    )


@pytest.mark.parametrize(
    "calculation",
    [
        "127.0.0.1",
        "cos(12.2)",
        "tan(sin(atan(cosh(1))))",
        "pie",
        "1+2*3/4^5%6",
        "gamma(17)",
        "hello",
        "1&2",
        "$13.50",
        "1::",
        "cos(tan(12+t+15))",
        "9 7",
    ],
)
def test_is_float_string__invalid(calculation):
    assert not Commons.is_float_string(calculation), (
        "Invalid string judged to be float, " + calculation
    )


@pytest.mark.parametrize(
    "calculation",
    ["0", "false", "off", "disabled", "disable", "", "nul", "null", "none", "nil"],
)
def test_is_string_null__valid(calculation):
    assert Commons.is_string_null(calculation), (
        "Valid string judged to be not null, " + calculation
    )


@pytest.mark.parametrize("calculation", ["true", "enable", "hello", "example", "test"])
def test_is_string_null__invalid(calculation):
    assert not Commons.is_string_null(calculation), (
        "Invalid string judged to be null, " + calculation
    )


def test_list_greater():
    try:
        Commons.list_greater([1] * 3, [1] * 5)
        assert (
            False
        ), "Function should throw an error if given 2 lists of unequal length."
    except ValueError:
        pass
    assert Commons.list_greater([5, 2, 1], [4, 2, 1])
    assert not Commons.list_greater([4, 2, 1], [5, 2, 1])
    assert Commons.list_greater([5, 2, 1], [4, 7, 9])
    assert not Commons.list_greater([4, 7, 9], [5, 2, 1])
    assert Commons.list_greater([1, 0, 0], [0, 9, 9])
    assert not Commons.list_greater([0, 9, 9], [1, 0, 0])
    assert Commons.list_greater([5, 3, 6], [5, 2, 6])
    assert not Commons.list_greater([5, 2, 6], [5, 3, 6])
    assert Commons.list_greater([5, 3, 6], [5, 3, 5])
    assert not Commons.list_greater([5, 3, 5], [5, 3, 6])
    assert Commons.list_greater(
        [1, 2, 3, 4, 5, 6, 7, 8, 10], [1, 2, 3, 4, 5, 6, 7, 8, 9]
    )
    assert not Commons.list_greater(
        [1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8, 10]
    )
    assert Commons.list_greater([1], [1]) is None
    assert Commons.list_greater([5, 2, 1], [5, 2, 1]) is None
    assert (
        Commons.list_greater([1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8, 9])
        is None
    )


@pytest.mark.parametrize("delta_string", ["20S, P20, P20S", "PTS"])
def test_load_time_delta__fail(delta_string):
    with pytest.raises(ISO8601ParseError):
        Commons.load_time_delta(delta_string)


@pytest.mark.parametrize(
    "delta_string, seconds, days",
    [("PT5S", 5, 0), ("P1T1S", 1, 1), ("P10T3600S", 3600, 10)],
)
def test_load_time_delta(delta_string, seconds, days):
    delta4 = Commons.load_time_delta(delta_string)
    assert delta4.seconds == seconds
    assert delta4.days == days


@pytest.mark.external_integration
def test_load_url_json():
    url1 = "https://httpbin.org/get"
    data1 = Commons.load_url_json(url1)
    assert "args" in data1, "Element missing from json dict response."
    assert "headers" in data1, "Element missing from json dict response."
    assert "origin" in data1, "Element missing from json dict response."
    assert "url" in data1, "Element missing from json dict response."
    assert data1["url"] == url1, "JSON data incorrect."
    url2 = "https://httpbin.org/headers"
    headers2 = [["User-Agent", "Example data"]]
    data2 = Commons.load_url_json(url2, headers2)
    assert "headers" in data2, "Element missing from json response dict."
    assert "User-Agent" in data2["headers"], "Header missing from request."
    assert (
        data2["headers"]["User-Agent"] == "Example data"
    ), "Header data missing from request."


@pytest.mark.external_integration
def test_load_url_string():
    url1 = "https://httpbin.org/get"
    data1 = Commons.load_url_string(url1)
    data1split = data1.split("\n")
    assert data1split[0] == "{", "First line incorrect."
    assert data1split[1] == '  "args": {}, ', "String response incorrect."
    url2 = "https://httpbin.org/headers"
    headers2 = [["User-Agent", "Example data"]]
    data2 = Commons.load_url_string(url2, headers2)
    data2split = data2.split("\n")
    assert data2split[0] == "{", "First line incorrect."
    assert data2split[1] == '  "headers": {', "String response incorrect."
    assert '"User-Agent": "Example data"' in data2, "Headers missing from request."


@pytest.mark.parametrize(
    "number, ordinal",
    [
        (1, "1st"),
        (2, "2nd"),
        (3, "3rd"),
        (4, "4th"),
        (5, "5th"),
        (10, "10th"),
        (11, "11th"),
        (12, "12th"),
        (13, "13th"),
        (14, "14th"),
        (20, "20th"),
        (21, "21st"),
        (22, "22nd"),
        (23, "23rd"),
        (24, "24th"),
        (100, "100th"),
        (101, "101st"),
        (102, "102nd"),
        (103, "103rd"),
        (104, "104th"),
        (111, "111th"),
        (121, "121st"),
    ],
)
def test_ordinal(number, ordinal):
    assert Commons.ordinal(number) == ordinal


def test_read_file_to_list():
    data = Commons.read_file_to_list("test/inc/test.txt")
    assert len(data) == 5
    assert data[0] == "test1"
    assert data[1] == "test2"
    assert data[2] == "test3"
    assert data[3] == "test4"
    assert data[4] == "test5"


@pytest.mark.parametrize(
    "string", ["1", "true", "t", "yes", "y", "on", "enabled", "enable"]
)
def test_string_to_bool__true(string):
    assert Commons.string_to_bool(string)


@pytest.mark.parametrize(
    "string", ["0", "false", "f", "no", "n", "off", "disabled", "disable"]
)
def test_string_to_bool__false(string):
    assert not Commons.string_to_bool(string)


@pytest.mark.parametrize("string", ["hello", "example", "test"])
def test_string_to_bool__none(string):
    assert Commons.string_to_bool(string) is None


def test_upper():
    assert Commons.upper("test words") == "TEST WORDS"


def test_upper__with_url():
    assert Commons.upper("test http://google.com url") == "TEST http://google.com URL"
