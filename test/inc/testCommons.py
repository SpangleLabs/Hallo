import re
import unittest

from datetime import timedelta, datetime

from inc.Commons import Commons, ISO8601ParseError


class CommonsTest(unittest.TestCase):

    def test_check_calculation(self):
        valid = ["23", "2.123", "cos(12.2)", "tan(sin(atan(cosh(1))))", "pie", "1+2*3/4^5%6", "gamma(17)"]
        invalid = ["hello", "1&2", "$13.50", "1::", "cos(tan(12+t+15))"]
        for valid_str in valid:
            assert Commons.check_calculation(valid_str), "Valid string judged to be not calculation, "+valid_str
        for invalid_str in invalid:
            assert not Commons.check_calculation(invalid_str), "Invalid string judged to be calculation, "+invalid_str

    def test_check_numbers(self):
        valid = ["23", "2.123", " 97", "9 7"]
        invalid = ["127.0.0.1", "cos(12.2)", "tan(sin(atan(cosh(1))))", "pie", "1+2*3/4^5%6", "gamma(17)", "hello",
                   "1&2", "$13.50", "1::", "cos(tan(12+t+15))"]
        for valid_str in valid:
            assert Commons.check_numbers(valid_str), "Valid string judged to be not calculation, "+valid_str
        for invalid_str in invalid:
            assert not Commons.check_numbers(invalid_str), "Invalid string judged to be calculation, "+invalid_str

    def test_chunk_string(self):
        chunks = Commons.chunk_string("a"*500, 100)
        assert len(chunks) == 5, "Did not return correct number of chunks"
        for chunk in chunks:
            assert len(chunk) <= 100, "Chunk of string is too long"
        chunks = Commons.chunk_string("", 100)
        assert len(chunks) == 0, "Did not handle empty string correctly."

    def test_chunk_string_dot(self):
        string1 = "a"*50
        chunks1 = Commons.chunk_string_dot(string1, 100)
        assert len(chunks1) == 1, "Should only be one chunk when splitting " + string1
        assert chunks1[0] == string1, "Should not have changed string " + string1
        string2 = "a"*100
        chunks2 = Commons.chunk_string_dot(string2, 100)
        assert len(chunks2) == 1, "Should only be one chunk when splitting " + string2
        assert chunks2[0] == string2, "Should not have changed string " + string2
        string3 = "a"*101
        chunks3 = Commons.chunk_string_dot(string3, 100)
        assert len(chunks3) == 2, "Should have split string into 2 chunks: " + string3
        assert len(chunks3[0]) == 100, "First chunk should be exactly 100 characters " + chunks3[0]
        assert chunks3[0] == "a"*97+"...", "First chunk of string was not created correctly"
        assert chunks3[1] == "..."+"a"*(101-97), "Second chunk of string was not created correctly."
        string4 = "a"*97*2
        chunks4 = Commons.chunk_string_dot(string4, 100)
        assert len(chunks4) == 2, "Should have split string into just 2 chunks."
        assert len(chunks4[0]) == 100, "First chunk should be exactly 100 characters"
        assert len(chunks4[1]) == 100, "Second chunk should be exactly 100 characters"
        assert chunks4[0] == "a"*97+"...", "First chunk of string was not created correctly"
        assert chunks4[1] == "..."+"a"*97, "Second chunk of string was not created correctly."
        string5 = "a"*(97*3-3)
        chunks5 = Commons.chunk_string_dot(string5, 100)
        assert len(chunks5) == 3, "Should have split string into 3 chunks"
        assert len(chunks5[0]) == 100, "First chunk should be 100 characters"
        assert len(chunks5[1]) == 100, "Second chunk should be 100 characters"
        assert len(chunks5[2]) == 100, "Third chunk should be 100 characters"
        assert chunks5[0] == "a"*97+"...", "First chunk created incorrectly."
        assert chunks5[1] == "..."+"a"*94+"...", "Second chunk created incorrectly."
        assert chunks5[2] == "..."+"a"*97, "Third chunk created incorrectly."
        string6 = "a"*(97*3-2)
        chunks6 = Commons.chunk_string_dot(string6, 100)
        assert len(chunks6) == 4, "Should have split string into 4 chunks"
        assert len(chunks6[0]) == 100, "First chunk should be 100 characters"
        assert len(chunks6[1]) == 100, "Second chunk should be 100 characters"
        assert len(chunks6[2]) == 100, "Third chunk should be 100 characters"
        assert chunks6[0] == "a"*97+"...", "First chunk created incorrectly"
        assert chunks6[1] == "..." + "a" * 94 + "...", "Second chunk created incorrectly"
        assert chunks6[2] == "..." + "a" * 94 + "...", "Third chunk created incorrectly"
        assert chunks6[3] == "..."+"a"*((97*3-2)-(94+94+97)), "Forth chunk created incorrectly"

    def test_current_timestamp(self):
        stamp = Commons.current_timestamp()
        assert len(stamp) == 10, "Timestamp is the wrong length"
        pattern = re.compile("^\[(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]\]$")
        assert pattern.match(stamp), "Timestamp is not valid to defined format."

    def test_current_timestamp_datetime_given(self):
        dtime = datetime(2019, 4, 6, 10, 15, 3)
        stamp = Commons.current_timestamp(dtime)
        assert stamp == "[10:15:03]"

    def test_format_time_delta(self):
        delta1 = timedelta(5, 5)
        assert Commons.format_time_delta(delta1) == "P5T5S"
        delta2 = timedelta(0, 50)
        assert Commons.format_time_delta(delta2) == "P0T50S"
        delta3 = timedelta(3, 0, 0, 0, 1)
        assert Commons.format_time_delta(delta3) == "P3T60S"
        delta4 = timedelta(2, 0, 0, 0, 0, 1)
        assert Commons.format_time_delta(delta4) == "P2T3600S"
        delta5 = timedelta(0, 0, 0, 0, 0, 0, 1)
        assert Commons.format_time_delta(delta5) == "P7T0S"

    def test_format_unix_time(self):
        unix1 = 0
        assert Commons.format_unix_time(unix1) == "1970-01-01 00:00:00"
        unix2 = 1000000000
        assert Commons.format_unix_time(unix2) == "2001-09-09 01:46:40"
        unix3 = 1234567890
        assert Commons.format_unix_time(unix3) == "2009-02-13 23:31:30"

    def test_get_calc_from_start_or_end(self):
        string1 = "$12*17"
        assert Commons.get_calc_from_start_or_end(string1) == "12*17", "Failed to get calculation from end"
        string2 = "cos(tan(12+t+15))"
        assert Commons.get_calc_from_start_or_end(string2) == "cos(tan(12+", "Failed to get calculation from start"
        string3 = "hello"
        assert Commons.get_calc_from_start_or_end(string3) is None, "Did not return None when no calculation found"
        string4 = "£13.50"
        assert Commons.get_calc_from_start_or_end(string4) == "13.50", "Failed to get number from end"
        string5 = "23f234"
        assert Commons.get_calc_from_start_or_end(string5) == "23", "Function should prioritise calculation at start"
        string6 = "tasty pie"
        assert Commons.get_calc_from_start_or_end(string6) == " pie", "Bit weird, but this should work too"

    def test_get_digits_from_start_or_end(self):
        string1 = "$12*17"
        assert Commons.get_digits_from_start_or_end(string1) == "17", "Failed to get digits from end"
        string2 = "cos(tan(12+t+15))"
        assert Commons.get_digits_from_start_or_end(string2) is None, "Should not have got any digits from string"
        string3 = "hello"
        assert Commons.get_digits_from_start_or_end(string3) is None, "Did not return None when no calculation found"
        string4 = "£13.50"
        assert Commons.get_digits_from_start_or_end(string4) == "13.50", "Failed to get number from end"
        string5 = "23f234"
        assert Commons.get_digits_from_start_or_end(string5) == "23", "Function should prioritise number at start"
        string6 = "tasty pie"
        assert Commons.get_digits_from_start_or_end(string6) is None, "Should not have got any digits from string"
        string7 = "2e7c"
        assert Commons.get_digits_from_start_or_end(string7) == "2e7", "Function should be able to get e notation"

    def test_domain_name(self):
        url1 = "https://github.com/joshcoales"
        assert Commons.get_domain_name(url1) == "github", "Failed to get domain from url1"
        url2 = "http://spangle.org.uk/things/stuff/hallo.html.com"
        assert Commons.get_domain_name(url2) == "spangle", "Failed to get domain from url2"
        url3 = "irc://irc.freenode.net:6666"
        assert Commons.get_domain_name(url3) == "freenode", "Failed to get domain from url3"
        url4 = "http://www.longurlmaker.com/go?id=143GetShortyShrtndspread%2Bout1tprotractedlongishYepItlofty1stretch" \
               "100RedirxMyURL1Sitelutionsspread%2Bout56706Ne1kfar%2Breachingstretchenlarged8U76SimURL01URLvi00distan" \
               "tr1towering46URLcutNe14m3q5stringy0elongatedremote7RubyURLRubyURL0300lasting52ny54blnk.inRedirx0t0aks" \
               "tretchedst765330DigBigf14922f8014v03121qeURl.ied99FhURL1MyURLFhURL8sustainedlingeringrunning07bYATUC6" \
               "8yU7618farawaystretchedxlfarawaySHurlcU760stretched01drangyccmstretchkrunningrremote52ganglingMyURL81" \
               "outstretchedTraceURL5aenduring60Is.gd5stretch69660Miniliengangling112vYATUC01drawn%2Bout29extensive1U" \
               "RLcutc03ShredURLfspread%2Boutoutstretched1EzURLTinyURLhigh0301URL7WapURL0u7Redirx5229NutshellURLdrawn" \
               "%2Boutwcfy68rangy4longish4SitelutionsG8LFwdURLe1stretchNanoRef56running2StartURLspun%2BoutShortURL165" \
               "MooURL4bTightURL00URLPieprolongedWapURLw0TightURL61runningdistantShorl8951hw2MooURLelongatek8lofty1Ti" \
               "nyURLc1qMetamark920bgelongate19n103c1dTinyLinkcontinuedlnk.in96591DecentURL0afar%2Breaching81elongish" \
               "504zremotec0l0e0adistants11high04DecentURL2stretchYATUCSnipURLstringys7b8deepTightURL1PiURLpa7elongat" \
               "edix0101Shim0Is.gdfar%2BreachingB65f8ctoweringNutshellURLWapURL1v9runningRubyURLURl.ie0ganglingEasyUR" \
               "L1ShortURL161stringy0h8extensivePiURL14prolongedEzURLt710distant1100rNanoRefh5311450ShrinkURLFwdURL1m" \
               "stretched119ganglingURLCuttera11fFhURL1b6tallFwdURLdlengthy110spun%2Bout7lastingf49Fly29loftyf5jXil0s" \
               "pread%2Bout4lengthyrangystretch8up0URL.co.uklingeringegURLHawk48zlengthyb3prolonged58loftyg18drawn%2B" \
               "outURLCutterURLHawk01cShortlinkshigh4remote1StartURLprolongedURLHawk0z03Shortlinks54gURLvi18elongated" \
               "EasyURL18elongated04WapURL1lofty51spread%2Bout1Redirx1A2N5411zfar%2Breachingf001prolonged01a4dstretch" \
               "sustainedoutstretchedShortURL612TraceURLURLvi00lasting28ec1URLcutcstringy827klengthyk1141DigBig9fcSHu" \
               "rl1Beam.toShorl0tstretchxURLCutterYepItnblasting080stretched1FhURL15rangy1x6600continuedShredURLblnk." \
               "inelongated00413outstretched0090146stretched589z05stringyc8sdielongatelongish6kprolongedfar%2Breachin" \
               "gf36ubaTinyURL1TinyLink341028017EasyURLd1runningfar%2Breaching06stretching1U76spun%2Bout1cstretch"
        assert Commons.get_domain_name(url4) == "longurlmaker", "Failed to get domain from url4"
        url5 = "http://domains.ninja"
        assert Commons.get_domain_name(url5) == "domains", "Failed to get domain from url5"

    def test_get_random_choice(self):
        for count in range(1, 3):
            for max_int in range(2, 10):
                for min_int in range(1, 5):
                    if min_int > max_int:
                        continue
                    input_list = list(range(min_int, max_int+1))
                    rand_list = Commons.get_random_choice(input_list, count)
                    assert len(rand_list) == count, "Random choice list is the wrong length. " + str(rand_list) + \
                                                    " not " + str(count) + " elements"
                    for rand in rand_list:
                        assert rand in input_list, "Random choice was not in the list. " + \
                                                   str(rand) + " not in " + str(input_list)

    def test_get_random_int(self):
        for count in range(1, 3):
            for max_int in range(2, 10):
                for min_int in range(1, 5):
                    if min_int > max_int:
                        continue
                    rand_list = Commons.get_random_int(min_int, max_int, count)
                    assert len(rand_list) == count, "Random integer list is the wrong length. " + str(rand_list) + \
                                                    " not " + str(count) + " elements"
                    for rand in rand_list:
                        assert rand >= min_int, "Random integer was too small. " + str(rand) + " < " + str(min_int)
                        assert rand <= max_int, "Random integer was too big. " + str(rand) + " > " + str(max_int)

    def test_is_float_string(self):
        valid = ["23", "2.123", " 97"]
        invalid = ["127.0.0.1", "cos(12.2)", "tan(sin(atan(cosh(1))))", "pie", "1+2*3/4^5%6", "gamma(17)", "hello",
                   "1&2", "$13.50", "1::", "cos(tan(12+t+15))", "9 7"]
        for valid_str in valid:
            assert Commons.is_float_string(valid_str), "Valid string judged to be not float, "+valid_str
        for invalid_str in invalid:
            assert not Commons.is_float_string(invalid_str), "Invalid string judged to be float, "+invalid_str

    def test_is_string_null(self):
        valid = ['0', 'false', 'off', 'disabled', 'disable', '', 'nul', 'null', 'none', 'nil']
        invalid = ["true", "enable", "hello", "example", "test"]
        for valid_str in valid:
            assert Commons.is_string_null(valid_str), "Valid string judged to be not null, "+valid_str
        for invalid_str in invalid:
            assert not Commons.is_string_null(invalid_str), "Invalid string judged to be null, "+invalid_str

    def test_list_greater(self):
        try:
            Commons.list_greater([1]*3, [1]*5)
            assert False, "Function should throw an error if given 2 lists of unequal length."
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
        assert Commons.list_greater([1, 2, 3, 4, 5, 6, 7, 8, 10], [1, 2, 3, 4, 5, 6, 7, 8, 9])
        assert not Commons.list_greater([1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8, 10])
        assert Commons.list_greater([1], [1]) is None
        assert Commons.list_greater([5, 2, 1], [5, 2, 1]) is None
        assert Commons.list_greater([1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 5, 6, 7, 8, 9]) is None

    def test_load_time_delta(self):
        string1 = "20S"
        try:
            Commons.load_time_delta(string1)
            assert False, "String 1 should have failed to parse."
        except ISO8601ParseError:
            pass
        string2 = "P20"
        try:
            Commons.load_time_delta(string2)
            assert False, "String 2 should have failed to parse."
        except ISO8601ParseError:
            pass
        string3 = "P20S"
        try:
            Commons.load_time_delta(string3)
            assert False, "String 3 should have failed to parse."
        except ISO8601ParseError:
            pass
        string4 = "PTS"
        delta4 = Commons.load_time_delta(string4)
        assert delta4.seconds == 0, "delta4 seconds set incorrectly."
        assert delta4.days == 0, "delta4 days set incorrectly."
        string5 = "P1T1S"
        delta5 = Commons.load_time_delta(string5)
        assert delta5.seconds == 1, "delta5 seconds set incorrectly."
        assert delta5.days == 1, "delta5 days set incorrectly."
        string6 = "P10T3600S"
        delta6 = Commons.load_time_delta(string6)
        assert delta6.seconds == 3600, "delta6 seconds set incorrectly."
        assert delta6.days == 10, "delta6 days set incorrectly."

    def test_load_url_json(self):
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
        assert data2["headers"]["User-Agent"] == "Example data", "Header data missing from request."

    def test_load_url_string(self):
        url1 = "https://httpbin.org/get"
        data1 = Commons.load_url_string(url1)
        data1split = data1.split("\n")
        assert data1split[0] == "{", "First line incorrect."
        assert data1split[1] == "  \"args\": {}, ", "String response incorrect."
        url2 = "https://httpbin.org/headers"
        headers2 = [["User-Agent", "Example data"]]
        data2 = Commons.load_url_string(url2, headers2)
        data2split = data2.split("\n")
        assert data2split[0] == "{", "First line incorrect."
        assert data2split[1] == "  \"headers\": {", "String response incorrect."
        assert "\"User-Agent\": \"Example data\"" in data2, "Headers missing from request."

    def test_ordinal(self):
        assert Commons.ordinal(1) == "1st", "1st ordinal incorrect."
        assert Commons.ordinal(2) == "2nd", "2nd ordinal incorrect."
        assert Commons.ordinal(3) == "3rd", "3rd ordinal incorrect."
        assert Commons.ordinal(4) == "4th", "4th ordinal incorrect."
        assert Commons.ordinal(5) == "5th", "5th ordinal incorrect."
        assert Commons.ordinal(10) == "10th", "10th ordinal incorrect."
        assert Commons.ordinal(11) == "11th", "11th ordinal incorrect."
        assert Commons.ordinal(12) == "12th", "12th ordinal incorrect."
        assert Commons.ordinal(13) == "13th", "13th ordinal incorrect."
        assert Commons.ordinal(14) == "14th", "14th ordinal incorrect."
        assert Commons.ordinal(20) == "20th", "20th ordinal incorrect."
        assert Commons.ordinal(21) == "21st", "21st ordinal incorrect."
        assert Commons.ordinal(22) == "22nd", "22nd ordinal incorrect."
        assert Commons.ordinal(23) == "23rd", "23rd ordinal incorrect."
        assert Commons.ordinal(24) == "24th", "24th ordinal incorrect."
        assert Commons.ordinal(100) == "100th", "100th ordinal incorrect."
        assert Commons.ordinal(101) == "101st", "101st ordinal incorrect."
        assert Commons.ordinal(102) == "102nd", "102nd ordinal incorrect."
        assert Commons.ordinal(103) == "103rd", "103rd ordinal incorrect."
        assert Commons.ordinal(104) == "104th", "104th ordinal incorrect."
        assert Commons.ordinal(111) == "111th", "111th ordinal incorrect."
        assert Commons.ordinal(121) == "121st", "121st ordinal incorrect."

    def test_read_file_to_list(self):
        data = Commons.read_file_to_list("test/inc/test.txt")
        assert len(data) == 5
        assert data[0] == "test1"
        assert data[1] == "test2"
        assert data[2] == "test3"
        assert data[3] == "test4"
        assert data[4] == "test5"

    def test_string_from_file(self):
        true_list = ['1', 'true', 't', 'yes', 'y', 'on', 'enabled', 'enable']
        for true_str in true_list:
            assert Commons.string_from_file(true_str)
        false_list = ['0', 'false', 'f', 'no', 'n', 'off', 'disabled', 'disable']
        for false_str in false_list:
            assert not Commons.string_from_file(false_str)
        null_list = ['', 'nul', 'null', 'none', 'nil']
        for null_str in null_list:
            assert Commons.string_from_file(null_str) is None
        invalid_list = ["hello", "example", "test"]
        for invalid_str in invalid_list:
            assert Commons.string_from_file(invalid_str) == invalid_str

    def test_string_to_bool(self):
        true_list = ['1', 'true', 't', 'yes', 'y', 'on', 'enabled', 'enable']
        for true_str in true_list:
            assert Commons.string_to_bool(true_str)
        false_list = ['0', 'false', 'f', 'no', 'n', 'off', 'disabled', 'disable']
        for false_str in false_list:
            assert not Commons.string_to_bool(false_str)
        invalid_list = ["hello", "example", "test"]
        for invalid_str in invalid_list:
            assert Commons.string_to_bool(invalid_str) is None

    def test_upper(self):
        assert Commons.upper("test words") == "TEST WORDS"
        assert Commons.upper("test http://google.com url") == "TEST http://google.com URL"
