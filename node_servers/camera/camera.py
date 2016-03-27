#!/usr/bin/python
#
# Install:
#  sudo pip install ipaddr
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
import os, json, logging, requests, threading, SocketServer, re, socket
from requests.auth import HTTPDigestAuth,HTTPBasicAuth
# Is there a better way to import these?  I'd rather import just this:
import camera_nodes
# And have all camera_nodes defined at the current level?  But have to import them all?
from camera_nodes import CameraServer
from logger import setup_log

global _REST_HANDLER
    

class CameraNodeServer(SimpleNodeServer):
    """ ISY Helper Camera Node Server """
    global _REST_HANDLER
    
    def setup(self):
        """ Initial node setup. """
        self.logger = setup_log(self.poly.sandbox,self.poly.name)
        self.logger.info('CameraNodeServer starting up.')
        self.logger.info("CameraNodeServer: Sandbox=%s" % (self.poly.sandbox))
        self.logger.info("CameraNodeServer: Config=%s" % (self.config))
        # define nodes for settings
        # Start a simple server for cameras to ping
        self.server = start_server(self)
        self.manifest = self.config.get('manifest', {})
        # Add the top level camera server node.
        CameraServer(self, "cams", "Camera Server", self.manifest)
        self.update_config()

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
        self.send_error("In camera query_node?");
        return True

    def long_poll(self):
        """ Save configuration every 30 seconds. """
        self.update_config()

    def on_exit(self, **kwargs):
        self.server.socket.close()
        return True

    def send_error(self,error_str):
        self.logger.error(error_str)
        self.poly.send_error(error_str);
        
    def motion(self,address,value):
        """ Poll Camera's  """
        self.logger.info("Got Motion for %s or %s" % (address, value) )
        if address in self.nodes:
            return self.nodes[address].motion(value)
        else:
            self.send_error("No node for motion on address %s" % (address));
        return False
    
    def http_get(self,ip,port,user,password,path,payload):
        url = "http://{}:{}/{}".format(ip,port,path)
        self.logger.debug("Sending: %s %s" % (url, payload) )
        auth = HTTPDigestAuth(user,password)
        try:
            response = requests.get(
                url,
                auth=auth,
                params=payload,
                timeout=10
            )
        except requests.exceptions.Timeout:
            self.send_error("Connection to the helper timed out")
            return False
        self.logger.debug("Got: %s", response.status_code)
        if response.status_code == 200:
            return response.text
        elif response.status_code == 400:
            self.send_error("Bad request: %s" % (url) )
        elif response.status_code == 404:
            self.send_error("Not Found: %s" % (url) )
        elif response.status_code == 401:
            # Authentication error
            self.send_error(
                "Failed to authenticate, please check your username and password")
        else:
            self.send_error("Unknown response %s: %s" % (response.status_code, url) )
        return False

class EchoRequestHandler(SocketServer.BaseRequestHandler):
    
    def handle(self):
        # Echo the back to the client
        data = self.request.recv(1024)
        # Don't worry about a status for now, just echo back.
        self.request.sendall(data)
        # Then parse it.
        myhandler(data)
        return

def get_network_ip(rhost):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((rhost, 0))
        return s.getsockname()[0]
    except:
        _SERVER.poly.send_error("get_network_ip: Failed to open socket to " + rhost)
        return False

def start_server(handler):
    global _REST_HANDLER
    myip = get_network_ip('8.8.8.8')
    address = (myip, 0) # let the kernel give us a port
    _REST_HANDLER = handler;
    server = SocketServer.TCPServer(address, EchoRequestHandler)
    #print "Running on: %s:%s" % server.server_address
    t = threading.Thread(target=server.serve_forever)
    #t.setDaemon(True) # don't hang on exit
    t.start()
    return server

def myhandler(data):
    #print "got: {}".format(data.strip())
    match = re.match( r'GET /motion/(.*) ', data, re.I)
    if match:
        address = match.group(1)
        _REST_HANDLER.motion(address,1)
    else:
        _REST_HANDLER.poly.send_error("Unrecognized socket server command: " + data)

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
