
#
# CameraServer
#
# This is the main Camera Node Server.  It was not really necessary to create
# this server but it will allow configuration params to be set and allow
# parsing the main config file or sending out upd requets to find cameras
# and automatically add them.
#
# TODO:
#  - Initialize cameras on started, Need a query for existing cameras, and discover for new cameras?
#  - Pass logger to foscam_poll
#  - Use GV3 to pass timeout to foscam_poll
#

from polyglot.nodeserver_api import Node
from Motion import Motion
from functools import partial
from foscam_poll import foscam_poll
from camera_nodes import *

def myint(value):
    """ round and convert to int """
    return int(round(float(value)))

CAMERA_SERVER_VERSION = 0.1

class CameraServer(Node):
    """ Node that contains the Main Camera Server settings """

    def __init__(self, parent, address, name, manifest=None):
        self.parent   = parent
        self.address  = address
        self.name     = name
        self.http_get = parent.http_get
        super(CameraServer, self).__init__(parent, self.address, self.name, True, manifest)        
        # The CameraServer Version number.
        self.set_driver('GV1', CAMERA_SERVER_VERSION, report=False)
        self.set_driver('GV2', 0, report=False)
        self.foscam_mjpeg = self.get_driver('GV3')[0]
        self.report_driver()
        #self.query();

    def query(self, **kwargs):
        """ Look for cameras """
        self.set_driver('GV1', CAMERA_SERVER_VERSION, report=True)
        num_cams = 0
        if self.foscam_mjpeg > 0:
            self.parent.logger.info("CameraServer: Polling for Foscam MJPEG cameras %s" % (self.foscam_mjpeg))
            cams = foscam_poll(self.parent.logger)
            self.parent.logger.info("CameraServer: Got cameras: " + str(cams))
            for cam in cams:
                self.parent.logger.info("CameraServer: Adding camera: %s:%s" % (cam['ip'], cam['port']))
                FoscamMJPEG(self.parent, True, cam['ip'], cam['port'], "polyglot", "poly*glot", self.manifest, cam['name'], cam['id'])
                num_cams += 1
                self.set_driver('GV2', num_cams, report=True)
            # Number of Cameras we are managing
            self.parent.logger.info("CameraServer: Done adding cameras")
        else:
            self.parent.logger.info("CameraServer: Not Polling for Foscam MJPEG cameras %s" % (self.foscam_mjpeg))
            self.set_driver('GV2', 0, report=True)
        return True

    def poll(self):
        """ Poll TODO: Ping the camera?  """
        return

    def _set_foscam_mjpeg(self, **kwargs):
        """ Enable/Disable Foscam MJPEG UDP Searching
              0 = Off
              0 = 10 second query
              0 = 20 second query
              0 = 30 second query
              0 = 60 second query
        """
        self.foscam_mjpeg = kwargs.get("value")
        self.parent.logger.info("CameraServer: Foscam Polling set to %s" % (self.foscam_mjpeg))
        self.set_driver('GV3', self.foscam_mjpeg, report=True)
        return True
    
    _drivers = {
        'GV1': [0, 56, float],
        'GV2': [0, 25, myint],
        'GV3': [0, 25, myint],
    }
    """ Driver Details:
    GV1: integer: This server version number
    GV2: integer: Number of the number of cameras we manage
    GV3: ingeger: foscam Polling
    """
    _commands = {
        'QUERY': query,
        'SET_FOSCAM_MJPEG': _set_foscam_mjpeg,
    }
    # The nodeDef id of this camers.
    node_def_id = 'CameraServer'

