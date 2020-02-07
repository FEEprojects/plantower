#!/usr/bin/env python3
"""
    Basic test script to demonstrate active mode of the plantower
"""
import plantower

#  test code for active mode
PLANTOWER = plantower.Plantower(port='COM3')
print(PLANTOWER.read())

