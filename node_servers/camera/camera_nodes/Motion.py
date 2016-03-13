
from polyglot.nodeserver_api import Node

def myint(value):
    """ round and convert to int """
    return int(round(float(value)))

class Motion(Node):
    """ Node that monitors motion """

    def __init__(self, parent, primary, manifest=None):
        self.name = primary.name + "-Motion"
        self.address = primary.address + "m";
        super(Motion, self).__init__(parent, self.address, self.name, primary, manifest)
        parent.add_node(self)

    def query(self, **kwargs):
        """ query the camera """
        # pylint: disable=unused-argument
        self.primary._get_status()
        # TODO: Should report only be true if it changes?
        self.set_driver('ST', self.primary.status['alarm_status'], report=True)
        return True

    def poll(self):
        """ Poll Motion  """
        return self.query()

    _drivers = {
        'ST': [0, 25, myint],
    }
    """ Driver Details:
    ST: Motion on/off
    """
    _commands = {
        'QUERY': query,
    }
    # The nodeDef id of this camers.
    node_def_id = 'CamMotion'
