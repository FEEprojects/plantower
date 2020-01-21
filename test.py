import plantower

#  test code for sleep wakeup with passive mode
pt = plantower.Plantower(port='COM3')

pt.set_to_sleep()
time.sleep(5)

pt.set_to_wakeup()
pt.mode_change(0)
time.sleep(10)

result = pt.read_in_passive()
pt.set_to_sleep()
print(result)
exit(0)


#  test code for passive mode
pt = plantower.Plantower(port='COM3')
pt.mode_change(0)
time.sleep(5)
result = pt.read_in_passive()
print(result)
exit(0)


#  test code for active mode
pt = plantower.Plantower(port='COM3')
print(pt.read())

