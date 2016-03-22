
# TODO:
#  - Set var alarm_http_url='http://192.168.1.66:25066/foscam/set.php';
#    To set device status on ISY.
#  - And var alarm_http=1;
#
from polyglot.nodeserver_api import Node
from Motion import Motion
from functools import partial

def myint(value):
    """ round and convert to int """
    return int(round(float(value)))

class FoscamMJPEG(Node):
    """ Node that contains the Hub connection settings """

    def __init__(self, parent, primary, ip_address, port, user, password, manifest=None):
        self.parent      = parent
        self.ip          = ip_address
        self.port        = port
        self.user        = user
        self.password    = password
        #
        # Get status which contains the camera id and alias.
        self._get_status()
        if not self.status:
            return None
        address  = self.status['id'].lower()
        name     = self.status['alias']
        # Add the Camera
        super(FoscamMJPEG, self).__init__(parent, address, name, primary, manifest)
        self._get_params();
        # Add my motion node.
        self.motion = Motion(parent, self, manifest)
        # Tell the camera to ping the parent server on motion.
        self._set_alarm_params({
            'motion_armed': 1,
            'http':         1,
            'http_url':     "http://%s:%s/motion/%s" % (parent.server.server_address[0], parent.server.server_address[1], self.motion.address)
        });
        # Call query to pull in the params.
        self.query();

    def query(self, **kwargs):
        """ query the camera """
        self._get_params();
        #self.parent.send_error("%s=%s" % ('alarm_motion_armed', self.params['alarm_motion_armed']) )        
        self.set_driver('GV1', self.params['alarm_motion_armed'], report=False) # ,uom=int, report=False ?
        self.set_driver('GV2', self.params['alarm_mail'], report=False)
        self.set_driver('GV3', self.params['alarm_motion_sensitivity'], report=False)
        self.set_driver('GV4', self.params['alarm_motion_compensation'], report=False)
        self.report_driver()
        # pylint: disable=unused-argument
        return True

    def _http_get(self, path, payload = {}):
        """ Call http_get on this camera for the specified path and payload """
        return self.parent.http_get(self.ip,self.port,self.user,self.password,path,payload)
        
    def _http_get_and_parse(self, path, payload = {}):
        """ 
        Call http_get and parse the returned Foscam data into a hash.  The data 
        is all looks like:  var id='000C5DDC9D6C';
        """
        data = self._http_get(path,payload)
        if data is False:
            return False
        ret  = {}
        for item in data.splitlines():
            param = item.replace('var ','').replace("'",'').strip(';').split('=')
            ret[param[0]] = param[1]
        return ret
    
    def _get_params(self):
        """ Call get_params on the camera and store in params """
        data = self._http_get_and_parse("get_params.cgi")
        self.params = data
        return data

    def poll(self):
        """ Nothing to poll?  We could poll to see if settings were manually changed?  """
        return

    def _set_alarm_params(self,params):
        """ 
        Set the sepecified params on the camera
        """
        return self._http_get("set_alarm.cgi",params)

    def _decoder_control(self,params):
        """ 
        Pass in decoder command
        """
        return self._http_get("decoder_control.cgi",params)

    def _get_status(self):
        """ 
        Call get_status on the camera and store in status
        """
        self.status = self._http_get_and_parse("get_status.cgi")

    def _set_alarm_param(self, driver=None, param=None, **kwargs):
        value = kwargs.get("value")
        if value is None:
            self.parent.send_error("_set_alarm_param not passed a value: %s" % (value) )
            return False
        # TODO: Should use the _driver specified function instead of int.
        if not self._set_alarm_params({ param: int(value)}):
            self.parent.send_error("_set_alarm_param failed to set %s=%s" % (param,value) )
        # TODO: Dont' think I should be setting the driver?
        self.set_driver(driver, value, report=True)
        # The set_alarm param is without the '_alarm' prefix
        self.params['alarm_'+param] = int(value)
        return True

    def _goto_preset(self, **kwargs):
        """ Goto the specified preset. 
              Preset 1 = Command 31
              Preset 2 = Command 33
              Preset 3 = Command 35
              Preset 16 = Command 61
              Preset 32 = Command 93
            So command is ((value * 2) + 29)
        """
        value = kwargs.get("value")
        if value is None:
            self.parent.send_error("_goto_preset not passed a value: %s" % (value) )
            return False
        value * 2 + 29
        value = myint((value * 2) + 29)
        if not self._decoder_control( { 'command': value} ):
            self.parent.send_error("_goto_preset failed to set %s" % (value) )
        return True

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
    _commands = {
        'QUERY': query,
        'SET_ALMOA': partial(_set_alarm_param, driver="GV1", param='motion_armed'),
        'SET_ALML':  partial(_set_alarm_param, driver="GV2", param='motion_mail'),
        'SET_ALMOS': partial(_set_alarm_param, driver="GV3", param='motion_sensitivity'),
        'SET_ALMOC': partial(_set_alarm_param, driver="GV4", param='motion_compensation'),
        'SET_POS':   _goto_preset,
    }
    # The nodeDef id of this camers.
    node_def_id = 'FoscamMJPEG'

