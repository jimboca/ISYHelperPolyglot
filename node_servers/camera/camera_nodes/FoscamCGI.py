
# TODO:
#  - Set var alarm_http_url='http://192.168.1.66:25066/foscam/set.php';
#    To set device status on ISY.
#  - And var alarm_http=1;
#
from polyglot.nodeserver_api import Node

def myint(value):
    """ round and convert to int """
    return int(round(float(value)))

class FoscamCGI(Node):
    """ Node that contains the Hub connection settings """

    def __init__(self, parent, ip_address, manifest=None):
        if ip_address == "192.168.1.110":
            self.name = "CameraFrontDoor"
            address   = "f000C5DDC9D6C"
        else:
            self.name = "CameraGarage"
            address   = "f00626E495BE9"
        self.address = address.lower()
        #print "FoscamCGI:init: " + nodeid + " " + name
        super(FoscamCGI, self).__init__(parent, self.address, self.name, True, manifest)
        self.ip = ip_address

    def query(self, **kwargs):
        """ query the camera """
        self.set_driver('GV1', 1) # ,uom=int, report=False ?
        self.set_driver('GV2', 2)
        self.set_driver('GV3', 3)
        self.set_driver('GV4', 4)
        # pylint: disable=unused-argument
        return True #self.parent.connect()

    _drivers = {
        'GV1': [0, 56, myint],
        'GV2': [0, 56, myint],
        'GV3': [0, 56, myint],
        'GV4': [0, 56, myint],
    }
    """ Driver Details:
    GV1: An integer
    GV2: An integer
    GV3: An integer
    GV4: An integer
    """
    _commands = {'QUERY': query}
    # The nodeDef id of this camers.
    node_def_id = 'FoscamCGI'
