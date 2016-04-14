import unittest

from Server import Server
from inc.Commons import Commons
from test.TestBase import TestBase


class CommonsTest(unittest.TestCase):

    def test_check_calculation(self):
        valid = ["23", "2.123", "cos(12.2)", "tan(sin(atan(cosh(1))))", "pie", "1+2*3/4^5%6", "gamma(17)"]
        invalid = ["hello", "1&2", "$13.50", "1::", "cos(tan(12+t+15))"]
        for valid_str in valid:
            assert Commons.check_calculation(valid_str), "Valid string judged to be not calculation, "+valid_str
        for invalid_str in invalid:
            assert not Commons.check_calculation(invalid_str), "Invalid string judged to be calculation, "+invalid_str

    def test_check_numbers(self):
        valid = ["23", "2.123"]
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
