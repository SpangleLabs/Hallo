import unittest

from Function import Function
from Server import Server
from test.TestBase import TestBase


class ProteinTest(TestBase, unittest.TestCase):

    def test_protein_simple(self):
        self.function_dispatcher.dispatch("protein ATTCATCGATCGCTA", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "ile-his-arg-ser-leu" in data[0][0].lower(), "Protein construction failed."

    def test_protein_start(self):
        self.function_dispatcher.dispatch("protein ATTCATCGAATGTCGCTA", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "start-ser-leu" in data[0][0].lower(), "Protein construction with start codon failed."

    def test_protein_stop(self):
        self.function_dispatcher.dispatch("protein ATTCATCGATAGTCGCTA", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "ile-his-arg-stop" in data[0][0].lower(), "Protein construction with stop codon failed."

    def test_protein_many_start(self):
        self.function_dispatcher.dispatch("protein ATTCATCGAATGTCGCTATGCATGCAGCATAUGCAGTCG",
                                          self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "start-gln-ser" in data[0][0].lower(), "Protein construction with multiple start codons failed."

    def test_protein_invalid(self):
        self.function_dispatcher.dispatch("protein ATGCATCGAATGTCGFTCAGCATAUGCAGTCG", self.test_user, self.test_user)
        data = self.server.get_send_data(1, self.test_user, Server.MSG_MSG)
        assert "error" in data[0][0].lower(), "Protein construction should fail with non-base characters."

    def test_protein_passive(self):
        self.function_dispatcher.dispatch_passive(Function.EVENT_MESSAGE, "ATTCATCGATCGCTA", self.server,
                                                  self.test_user, self.test_chan)
        data = self.server.get_send_data(1, self.test_chan, Server.MSG_MSG)
        assert"ile-his-arg-ser-leu" in data[0][0].lower(), "Passive protein construction failed."
