#!/usr/bin/env python3
"""
    Basic test script to demonstrate passive mode with fan turn off for  the plantower
"""
import time
import plantower
#  test code for sleep wakeup with passive mode
PLANTOWER = plantower.Plantower(port='COM3')

PLANTOWER.set_to_sleep() #Stop the fan in the sensor
time.sleep(5)

PLANTOWER.set_to_wakeup() # Start the fan in the sensor
PLANTOWER.mode_change(plantower.PMS_PASSIVE_MODE)
time.sleep(30) # Give the readings a chance to settle after fan spin up
#30s is suggested in the datasheet

RESULT = PLANTOWER.read_in_passive() # request data in passive mode
PLANTOWER.set_to_sleep() # turn fan off again
print(RESULT)
