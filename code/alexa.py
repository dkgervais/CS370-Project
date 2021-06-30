                                                                                                    

import json
from agt import AlexaGadget
import aqnb
import sys
import logging

# Necessary to allow printing out of bluetooth info
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

class MyGadget(AlexaGadget):

    def __init__(self):
        super().__init__()

    # Function that receives a payload from Alexa 
    def on_custom_mygadget_pitoalexa(self, directive):
        payload = {'data': "Air Quality is " + aqnb.get_air_quality()}
        # Send the payload in the event back to Alexa
        self.send_custom_event('Custom.MyGadget', 'PiToAlexa', payload)

MyGadget().main()

