import random

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
