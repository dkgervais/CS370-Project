#
# Copyright 2019 Amazon.com, Inc. or its affiliates.  All Rights Reserved.
# These materials are licensed under the Amazon Software License in connection with the Alexa Gadgets Program.
# The Agreement is available at https://aws.amazon.com/asl/.
# See the Agreement for the specific terms and conditions of the Agreement.
# Capitalized terms not defined in this file have the meanings given to them in the Agreement.
#

import logging
import sys
from air_quality import calculate_air_quality

from agt import AlexaGadget

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

class WakewordGadget(AlexaGadget):
    """
    An Alexa Gadget that calculates indoor air quality with the detection
    of the wake word
    """

    def __init__(self):
        super().__init__()

    def on_alexa_gadget_statelistener_stateupdate(self, directive):
        for state in directive.payload.states:
            if state.name == 'wakeword':
                air_quality_index = calculate_air_quality()
                # TODO: Add functionality to pass air quality index 
                # back to Alexa


if __name__ == '__main__':
    try:
        WakewordGadget().main()
