#!/usr/bin/env python3
"""
    Basic test script to demonstrate passive mode of the plantower
"""
import time
import plantower

PLANTOWER = plantower.Plantower(port='COM3') # create the object

PLANTOWER.mode_change(plantower.PMS_PASSIVE_MODE) #change into passive mode
time.sleep(5) #give the sensor a chance to settle
RESULT = PLANTOWER.read_in_passive() # request data in passive mode
print(RESULT)
