  GNU nano 3.2                                                                             my_gadget.py                                                                                       

import json
from agt import AlexaGadget
import sys
import logging

# Necessary to allow printing out of bluetooth info
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

# YOUR CODE HERE
def get_reading(sensor_num):
    print(sensor_num)
    if int(sensor_num) == 1:
        return 100.0
    else:
        return 0.0

class MyGadget(AlexaGadget):

    def __init__(self):
        super().__init__()


    # Function that recieves a payload from Alexa 
    def on_custom_mygadget_pitoalexa(self, directive):
        # Parse the payload sent in on the directive
        # This payload will contain all of the slot values from the
        # intent that was assigned in the Alexa Developer Console
        payload = json.loads(directive.payload.decode("utf-8"))
        # Print out the payload
        print("Received data: " + str(payload))
        # Construct a response event to send back to Alexa using (or not using)
        # the data sent in with the payload from the directive
        # NOTE: Alexa Cloud functions such that whatever you send
        # out in the event payload in this file will be spoken by Alexa when it is recieved
        payload = {'data': "The sensor reads, " + str(get_reading(payload['data']['sensor_num']['value'])) + " (some value)."}
        # Send the payload in the event back to Alexa
        self.send_custom_event('Custom.MyGadget', 'PiToAlexa', payload)

MyGadget().main()
