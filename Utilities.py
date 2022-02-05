import math
import random
from ConfigReader import ConfigData as config

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

#Clamp a value to range (min,max)
def clamp(min,max,value):
    if value < min:
        return min
    if value > max:
        return max
    return value

#check if a list has duplicates
def ListHasDuplicates(inputlist):
    if len(inputlist) == len(set(inputlist)):
        return False
    else:
        return True 


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

#count the number of places for a given number
def countPlaces(number):
    count = 0
    while number != 0:
        number //= 10
        count += 1
    return count

#gets a repeatable random number given the current tick and the config seed
def getRandomValue(currentTime,min,max):
    seed = config.getint("VALUES","SEED")
    random.seed(seed/(convertTimeToTicks(currentTime)+1))
    result = random.randint(min,max)
    return result
