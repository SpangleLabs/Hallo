import re

from inc.commons import Commons


class InputParser:

    def __init__(self, raw_input):
        """
        :type raw_input: str
        """
        self.args_dict = dict()
        self.remaining_text = raw_input
        self.number_words = []
        self.string_words = []
        self.parse_args()
        self.parse_words()

    def parse_args(self):
        regexes = [re.compile(r"([\"'])(?P<key>[^=]+?)\1=([\"'])(?P<value>.*?)\3"),  # quoted key, quoted args
                   re.compile(r"(?P<key>[^\s]+)=([\"'])(?P<value>.*?)\2"),  # unquoted key, quoted args
                   re.compile(r"([\"'])(?P<key>[^=]+?)\1=(?P<value>[^\s]*)"),  # quoted key, unquoted args
                   re.compile(r"(?P<key>[^\s]+)=(?P<value>[^\s]*)")]  # unquoted key, unquoted args
        for regex in regexes:
            for match in regex.finditer(self.remaining_text):
                self.args_dict[match.group("key")] = match.group("value")
                self.remaining_text = self.remaining_text.replace(match.group(0), "")
        # Clean double spaces and trailing spaces.
        self.remaining_text = " ".join(self.remaining_text.split())

    def parse_words(self):
        for word in self.remaining_text.split():
            if Commons.is_float_string(word):
                self.number_words.append(float(word))
            else:
                self.string_words.append(word)

    def get_arg_by_names(self, names_list):
        for name in names_list:
            if name in self.args_dict:
                return self.args_dict[name]
        return None

    def split_remaining_into_two(self, verify_pair_func):
        """
        Splits the remaining text, into pairs of text, where the first half matches the verify function, and the second
        half is the rest.
        :param verify_pair_func: Function which verifies if a text pair is potentially valid
        :type verify_pair_func: (string, string) -> bool
        :return: List of pairs of strings
        :rtype: list[list[str]]
        """
        line_split = self.remaining_text.split()
        if len(line_split) <= 1:
            return []
        # Start splitting from shortest left-string to longest.
        input_sections = [[" ".join(line_split[:x + 1]),
                           " ".join(line_split[x + 1:])]
                          for x in range(len(line_split) - 1)]
        results = []
        for input_pair in input_sections:
            # Check if the first input of the pair matches any units
            if verify_pair_func(input_pair[0], input_pair[1]):
                results.append([input_pair[0], input_pair[1]])
            # Then check if the second input of the pair matches any units
            if verify_pair_func(input_pair[1], input_pair[0]):
                results.append([input_pair[1], input_pair[0]])
        return results
