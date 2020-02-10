#!/usr/bin/env python3
"""
    Basic test script to demonstrate active mode of the plantower
"""

from argparse import ArgumentParser
import time
import plantower


PARSER = ArgumentParser(
        description="Test plantower code in active mode")
PARSER.add_argument(
    "port",
    action="store",
    help="The serial port to use")
ARGS = PARSER.parse_args()

#  test code for active mode
PLANTOWER = plantower.Plantower(port=ARGS.port)
print("Making sure it's correctly setup for active mode. Please wait")
#make sure it's in the correct mode if it's been used for passive beforehand
#Not needed if freshly plugged in
PLANTOWER.mode_change(plantower.PMS_ACTIVE_MODE) #change back into active mode
PLANTOWER.set_to_wakeup() #ensure fan is spinning
time.sleep(30) # give it a chance to stabilise
#actually do the reading
print(PLANTOWER.read())
