#!/usr/bin/python

#
# Issues:
#  - Once the node is registered, it's name will not change.
#
""" Camera Node Server for ISY """

try:
    from httplib import BadStatusLine  # Python 2.x
except ImportError:
    from http.client import BadStatusLine  # Python 3.x
from polyglot.nodeserver_api import SimpleNodeServer, PolyglotConnector
from collections import defaultdict, OrderedDict
import os
import socket
# Is there a better way to import these?  I'd rather import just this:
import camera_nodes
# And have all camera_nodes defined at the current level?  But have to import them all?
from camera_nodes import *

class CameraNodeServer(SimpleNodeServer):
    """ ISY Helper Camera Node Server """

    def setup(self):
        """ Initial node setup. """
        # define nodes for settings
        self.manifest = self.config.get('manifest', {})
        self.add_node(FoscamCGI(self, "192.168.1.110", self.manifest))
        self.add_node(FoscamCGI(self, "192.168.1.111", self.manifest))
        #self.connect()
        self.update_config() # not in NodeServer? Only SimpleNodeServer

    def connect(self):
        """ TODO: Connect to Camera to get it's name """
        # pylint: disable=broad-except
        return True

    def poll(self):
        """ Poll Camera  """
        return True

    def query_node(self, lkp_address):
        return True

    def long_poll(self):
        """ Save configuration every 30 seconds. """
        #self.update_config()


def main():
    """ setup connection, node server, and nodes """
    poly = PolyglotConnector()
    nserver = CameraNodeServer(poly)
    poly.connect()
    poly.wait_for_config()
    nserver.setup()
    nserver.run()


if __name__ == "__main__":
    main()
