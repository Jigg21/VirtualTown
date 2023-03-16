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

#count the number of decimal places for a given number
def countPlaces(number):
    count = 0
    while number != 0:
        number //= 10
        count += 1
    return count

def initialIzeRandomSeed():
    '''seed the random function'''
    seed = config.getint("VALUES","SEED")
    random.seed(seed)

def getRandomValue(min,max):
    '''get a random number between min and max, inclusive'''
    result = random.randint(min,max)
    return result

def truncateDecimal(f,places):
    result =  f * 10**places
    result //= 10**places
    return result


def coordsInRange(upperCorner,lowerCorner,Coord):
    '''returns true if coord is within a box defined by upperCorner and lowerCorner
        coords should be given in a tuple of ints'''
    x = upperCorner[0] <= Coord[0] and Coord[0] <= lowerCorner[0]
    y = upperCorner[1] >= Coord[1] and Coord[1] >= lowerCorner[1]
    return x and y
