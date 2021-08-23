import random

#converts readable time to ticks
def convertTimeToTicks(timeString):
    timeSplit = timeString.split(":")
    cycles = 0
    #Years
    cycles += int(timeSplit[0])*525600
    #Days
    cycles += int(timeSplit[1])*1440
    #Hours
    cycles += int(timeSplit[2]*60)
    #Minutes
    cycles += int(timeSplit[3])

    return cycles

#converts ticks to a readable time
def convertTicksToTime(time):
    workingTime = time
    result = ""
    result += str(time//525600) + ":"
    time%=525600
    result += str(time//1440) + ":"
    time%=1440
    result += str(time//60) + ":"
    time%=60
    result += str(time%60)
    return result

#takes float from 0.0 to 1.0 and displays color gradient equivalent in hex
def interpolateRedtoGreen(amount):
    return "#ff0000"
    if (amount == 0):
        return "#ff0000"
    r,g = 0,0
    if amount < .5:
        g = 510 * amount
    else:
        g = 255
        r = (1-amount) * 510
    return '#%02x%02x%02x' % (int(r), int(g), 0)