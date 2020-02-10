#!/usr/bin/env python3
"""
    Basic test script to demonstrate passive mode with fan turn off for  the plantower
"""
import time
from argparse import ArgumentParser
import plantower


PARSER = ArgumentParser(
        description="Test plantower code in passive mode with fan turn off")
PARSER.add_argument(
    "port",
    action="store",
    help="The serial port to use")
ARGS = PARSER.parse_args()


PLANTOWER = plantower.Plantower(port=ARGS.port)
print("Turning off the fan for 15s")
PLANTOWER.set_to_sleep() #Stop the fan in the sensor
time.sleep(15)
print("Waking back up. Please wait")
PLANTOWER.set_to_wakeup() # Start the fan in the sensor
PLANTOWER.mode_change(plantower.PMS_PASSIVE_MODE)
time.sleep(30) # Give the readings a chance to settle after fan spin up
#30s is suggested in the datasheet

RESULT = PLANTOWER.read_in_passive() # request data in passive mode
PLANTOWER.set_to_sleep() # turn fan off again
print(RESULT)
