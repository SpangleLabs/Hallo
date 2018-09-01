import unittest

from Events import EventMessage
from test.TestBase import TestBase


class ProteinTest(TestBase, unittest.TestCase):

    def test_protein_simple(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "protein ATTCATCGATCGCTA"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "ile-his-arg-ser-leu" in data[0].text.lower(), "Protein construction failed."

    def test_protein_start(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "protein ATTCATCGAATGTCGCTA"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "start-ser-leu" in data[0].text.lower(), "Protein construction with start codon failed."

    def test_protein_stop(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user, "protein ATTCATCGATAGTCGCTA"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "ile-his-arg-stop" in data[0].text.lower(), "Protein construction with stop codon failed."

    def test_protein_many_start(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "protein ATTCATCGAATGTCGCTATGCATGCAGCATAUGCAGTCG"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "start-gln-ser" in data[0].text.lower(), "Protein construction with multiple start codons failed."

    def test_protein_invalid(self):
        self.function_dispatcher.dispatch(EventMessage(self.server, None, self.test_user,
                                                       "protein ATGCATCGAATGTCGFTCAGCATAUGCAGTCG"))
        data = self.server.get_send_data(1, self.test_user, EventMessage)
        assert "error" in data[0].text.lower(), "Protein construction should fail with non-base characters."

    def test_protein_passive(self):
        self.function_dispatcher.dispatch_passive(EventMessage(self.server, self.test_chan, self.test_user,
                                                               "ATTCATCGATCGCTA"))
        data = self.server.get_send_data(1, self.test_chan, EventMessage)
        assert"ile-his-arg-ser-leu" in data[0].text.lower(), "Passive protein construction failed."
