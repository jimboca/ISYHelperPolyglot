
#
# CameraServer
#
# This is the main Camera Node Server.  It was not really necessary to create
# this server but it will allow configuration params to be set and allow
# parsing the main config file or sending out upd requets to find cameras
# and automatically add them.
#
#

from polyglot.nodeserver_api import Node
from Motion import Motion
from functools import partial

from camera_nodes import *

def myint(value):
    """ round and convert to int """
    return int(round(float(value)))

class CameraServer(Node):
    """ Node that contains the Main Camera Server settings """

    def __init__(self, parent, address, name, manifest=None):
        self.parent   = parent
        self.address  = address
        self.name     = name
        self.http_get = parent.http_get
        super(CameraServer, self).__init__(parent, self.address, self.name, True, manifest)
        # The CameraServer Version number.
        self.set_driver('GV1', 1, report=True) # ,uom=int,
        self.query();

    def query(self, **kwargs):
        """ Look for cameras """
        FoscamMJPEG(self.parent, True, "192.168.1.110", "8080", "admin", "diabl099", self.manifest)
        FoscamMJPEG(self.parent, True, "192.168.1.111", "8080", "admin", "diabl099", self.manifest)
        FoscamMJPEG(self.parent, True, "192.168.1.112", "8080", "admin", "diabl099", self.manifest)
        # Number of Cameras we know about.
        self.set_driver('GV2', 3, report=True) # ,uom=int,
        return True

    def poll(self):
        """ Poll ?  """
        return

    _drivers = {
        'GV1': [0, 56, myint],
    }
    """ Driver Details:
    GV1: An Boolean
    """
    _commands = {
        'QUERY': query,
    }
    # The nodeDef id of this camers.
    node_def_id = 'CameraServer'

