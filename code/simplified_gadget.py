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

# TODO: Change Intent pi_to_alexa, remove sensor_data in Intent Slot, update Sample Utterances
# https://developer.amazon.com/alexa/console/ask
# Necessary to allow printing out of bluetooth info
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

# Simulate reading a sensor, return value must be string for  
# JSON payload back to Skill
def get_reading():
        # YOUR CODE HERE
        return 'whatever your heart desires'

class MyGadget(AlexaGadget):
    def __init__(self):
        super().__init__()
    # Function that recieves a payload from Alexa 
    # NOTE: Version where no data sent from Skill, just invokes 
    # get_reading() function
    def on_custom_mygadget_pitoalexa(self, directive):
        # Alexa JSON callback speech data, return value must be string
        payload = {'data': "Air Quality is, " + str(get_reading()) + ", some unit."}
        print("Callback data: " + str(payload))
         # Send the JSON payload in the event back to Alexa 
        self.send_custom_event('Custom.MyGadget', 'PiToAlexa', payload)

MyGadget().main()
