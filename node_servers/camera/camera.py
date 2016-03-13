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
import json
import logging
import requests
from requests.auth import HTTPDigestAuth,HTTPBasicAuth
# Is there a better way to import these?  I'd rather import just this:
import camera_nodes
# And have all camera_nodes defined at the current level?  But have to import them all?
from camera_nodes import *

_LOGGER = logging.getLogger(__name__)

class CameraNodeServer(SimpleNodeServer):
    """ ISY Helper Camera Node Server """

    def setup(self):
        """ Initial node setup. """
        # define nodes for settings
        _LOGGER.info("setup:")
        self.manifest = self.config.get('manifest', {})
        FoscamCGI(self, "192.168.1.110", "8080", "admin", "diabl099", self.manifest)
        FoscamCGI(self, "192.168.1.111", "8080", "admin", "diabl099", self.manifest)
        FoscamCGI(self, "192.168.1.112", "8080", "admin", "diabl099", self.manifest)
        #self.connect()
        self.update_config() # not in NodeServer? Only SimpleNodeServer

    def connect(self):
        """ TODO: Connect to Camera to get it's name """
        # pylint: disable=broad-except
        return True

    def poll(self):
        """ Poll Camera's  """
        for node_addr, node in self.nodes.items():
            node.poll()
        return True

    def query_node(self, address):
        # This is never called, only if child node calls it?
        self.poly.send_error("In camera query_node");
        return True

    def long_poll(self):
        """ Save configuration every 30 seconds. """
        #self.update_config()

    def http_get(self,ip,port,user,password,path,payload):
        url = "http://{}:{}/{}".format(ip,port,path)
        #_LOGGER.info("http_get:send: " + url)
        #self.poly.send_error("Sending: %s %s" % (url, payload) )
        auth = HTTPDigestAuth(user,password)
        try:
            response = requests.get(
                url,
                auth=auth,
                params=payload,
                timeout=10
            )
        except requests.exceptions.Timeout:
            self.poly.send_error("Connection to the helper timed out")
            return False
        #_LOGGER.info("http_get:response: " + response.url)
        if response.status_code == 200:
            return response.text
        elif response.status_code == 400:
            self.poly.send_error("Bad request: %s" % (url) )
        elif response.status_code == 404:
            self.poly.send_error("Not Found: %s" % (url) )
        elif response.status_code == 401:
            # Authentication error
            self.poly.error(
                "Failed to authenticate, please check your username and password")
        else:
            self.poly.send_error("Unknown response %s: %s" % (response.status_code, url) )
        return False

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
