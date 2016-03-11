""" Node classes used by the ISY Helper Camera Node Server. """

from polyglot.nodeserver_api import Node
from functools import partial
#import json
#import urllib2


def myint(value):
    """ round and convert to int """
    return int(round(float(value)))

def myfloat(value, prec=4):
    """ round and return float """
    return round(float(value), prec)


from .FoscamCGI import FoscamCGI

class CameraServer(Node):
    """ Node that contains the Hub connection settings """

    def __init__(self, parent, manifest=None):
        super(CameraServer, self).__init__(parent, "camserve", "CameraServer", manifest)

    def query(self, **kwargs):
        """ query the camera """
        self.set_driver('GV1', 1) # ,uom=int, report=False ?
        return True #self.parent.connect()

    _drivers = {
        'GV1': [0, 56, myint],
    }
    _commands = {}
    # The nodeDef id of this camers.
    node_def_id = 'CAMSERVER'
