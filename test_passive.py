#!/usr/bin/env python3
"""
    Basic test script to demonstrate passive mode of the plantower
"""
from argparse import ArgumentParser
import time
import plantower


PARSER = ArgumentParser(
        description="Test plantower code in passive mode")
PARSER.add_argument(
    "port",
    action="store",
    help="The serial port to use")
ARGS = PARSER.parse_args()


PLANTOWER = plantower.Plantower(port=ARGS.port) # create the object

PLANTOWER.mode_change(plantower.PMS_PASSIVE_MODE) #change into passive mode
time.sleep(5) #give the sensor a chance to settle
RESULT = PLANTOWER.read_in_passive() # request data in passive mode
print(RESULT)
