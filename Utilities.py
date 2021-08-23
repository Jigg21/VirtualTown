import math
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

def clamp(min,max,value):
    if value < min:
        return min
    if value > max:
        return max
    return value


#takes float from 0.0 to 1.0 and displays color gradient equivalent in hex
def interpolateRedtoGreen(amount):
    r,g,b = 0,0,0
    if amount < .5:
        r = 255
        g = 510 * amount
    elif amount >= .5 and amount <= 1:
        g = 255
        r = (1-amount) * 510
    elif amount > 1:
        g = 255
        b =  255 * (1-amount)/.3
    
    r = clamp(0,255,r)
    g = clamp(0,255,g)
    b = clamp(0,255,b)
    return '#%02x%02x%02x' % (int(r), int(g), int(b))