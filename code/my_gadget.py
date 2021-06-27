#
# Copyright 2019 Amazon.com, Inc. or its affiliates.  All Rights Reserved.
# These materials are licensed under the Amazon Software License in connection with the Alexa Gadgets Program.
# The Agreement is available at https://aws.amazon.com/asl/.
# See the Agreement for the specific terms and conditions of the Agreement.
# Capitalized terms not defined in this file have the meanings given to them in the Agreement.
#

import json
from agt import AlexaGadget
import sys
import logging

# Necessary to allow printing out of bluetooth info
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to simulate reading a sensor for users with nothing wired yet
# YOUR CODE HERE
def get_temp(sensor_num):
    print(sensor_num)
    if int(sensor_num) == 1:
        return 100.0
    else:
        return 0.0

class MyGadget(AlexaGadget):

    def __init__(self):
        super().__init__()


    # Function that recieves a payload from Alexa 
    # and then sends one back within 5 seconds.
    def on_custom_mygadget_pitoalexa(self, directive):
        # Parse the payload sent in on the directive
        # NOTE: This payload will contain all of the slot values from the
        # intent that was used
        payload = json.loads(directive.payload.decode("utf-8"))
        # Print out the payload
        print("Received data: " + str(payload))
        # Construct a response event to send back to Alexa using (or not using)
        # the data sent in with the payload from the directive
        # NOTE: I have constructed the cloud functions such that whatever you send
        # out in the event payload here will be spoken by Alexa when it is recieved
        payload = {'data': "Check it out, " + str(get_temp(payload['data']['sensor_num']['value'])) + " degrees."}
        # Send the payload in the event back to Alexa
        self.send_custom_event('Custom.MyGadget', 'PiToAlexa', payload)
        
MyGadget().main()
