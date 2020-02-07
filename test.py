#!/usr/bin/env python3
"""
    Basic test script to demonstrate active mode of the plantower
"""

from argparse import ArgumentParser
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
print(PLANTOWER.read())

