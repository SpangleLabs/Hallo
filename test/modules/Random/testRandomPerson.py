import re
import unittest

from Events import EventMessage
from test.TestBase import TestBase


class RandomPersonTest(TestBase, unittest.TestCase):

    def test_person(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "random person"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "i have generated this person" in data[0].text.lower(), "Should state that a person is generated."
        name_regex = re.compile(r"say hello to .+\.", re.IGNORECASE)
        assert name_regex.search(data[0].text) is not None, "Name should stated and not be blank."
        pronoun_dob_regex = re.compile(r"s?he was born at [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.", re.I)
        assert pronoun_dob_regex.search(data[0].text) is not None, "Pronoun and date of birth should be used."

    def test_person_full(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "random person verbose"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "i have generated this person" in data[0].text.lower(), "Should state that a person is generated."
        name_regex = re.compile(r"say hello to .+\.", re.IGNORECASE)
        assert name_regex.search(data[0].text) is not None, "Name should stated and not be blank."
        pronoun_dob_regex = re.compile(r"(s?he) was born at [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} "
                                       r"and lives at .+\.", re.I)
        assert pronoun_dob_regex.search(data[0].text) is not None, "Pronoun, date of birth and address should be used."
        pronoun = pronoun_dob_regex.search(data[0].text).group(1)
        assert "{} uses the email".format(pronoun) in data[0].text, "Pronoun use is not consistent."
        pronoun_posessive = "Her" if pronoun.lower() == "she" else "His"
        assert "{} home number is".format(pronoun_posessive) in data[0].text, "Possessive pronoun is not correct."
        email_regex = re.compile(r"uses the email (.+@.+),")
        assert email_regex.search(data[0].text) is not None, "Email not given."
        assert len(email_regex.search(data[0].text).group(1)) > 2, "Email should be at least 3 characters"
        username_regex = re.compile(r"the username .+ and")
        assert username_regex.search(data[0].text) is not None, "Username not given."
        password_regex = re.compile(r"uses the password \".+\"")
        assert password_regex.search(data[0].text) is not None, "Password cannot be blank."
        home_numer_regex = re.compile(r"home number is [0-9 ]+ but")
        assert home_numer_regex.search(data[0].text) is not None, "Home number not given."
        mob_number_regex = re.compile(r"mobile number is [0-9-]+\.")
        assert mob_number_regex.search(data[0].text) is not None, "Mobile number not given."
        NI_regex = re.compile(r"national insurance number is [A-Z]{2} [0-9]{2} [0-9]{2} [0-9]{2} [A-Z]\.")
        assert NI_regex.search(data[0].text) is not None, "National insurance number not given."
