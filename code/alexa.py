import sys
from air_quality import calculate_air_quality

from agt import AlexaGadget

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
