import unittest

from test.TestBase import TestBase


class ConnectTest(TestBase, unittest.TestCase):

    def test_no_args(self):
        return True


# Todo, tests to write:
# Check tests are okay
# See if I can locate the search intermittent failure?
# test Connect to known server
# test Connect to known server fail already connected
# test Connect fail unrecognised protocol
# test Connect default to current type
# test Connect specify irc
# port in url
# port by argument
# address by argument
# address in argument
# inherit port
# non-int port
# null address
# specified server name
# get server name from domain
# auto connect true
# auto connect false
# auto connect default true
# server nick specified
# server nick inherit
# server prefix specified
# server prefix inherit
# full name specified
# full name inherit
# nickserv nick default
# nickserv nick inherit
# nickserv nick specified
# nickserv identity command default
# nickserv identity command inherit
# nickserv identity command specified
# nickserv identity resp default
# nickserv identity resp inherit
# nickserv identity resp specified
# nickserv password default
# nickserv password inherit
# nickserv password specified
# set groups of current user on other server
# check server added
# check thread started
# check server started
