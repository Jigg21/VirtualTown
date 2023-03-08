import random
import os
import sys
root_folder = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_folder)

import CONST

def generatePath(culture):
    cultureFile = "data/Cultures/"
    if culture == CONST.cultures.ROMAN:
        cultureFile += "Roman/"
    if culture == CONST.cultures.NOMAD:
        cultureFile += "Nomadic/"
    if culture == CONST.cultures.LIBERTARIAD:
        cultureFile += "Libertariad/"
    return cultureFile 
#generate a name from the nameGen.txt file
def makeName(culture):
    sets = []
    #open the syllable file 
    cultureFolderPath = generatePath(culture)
    with open(cultureFolderPath+"nameGen.txt") as f:
        sets = []
        set = []
        pos = 0
        #write in lines until it reaches a syllable boundary (limits on which syllables appear in which part of the name)
        for line in f.readlines():
            #reached a boundary
            if line[0] == "$":
                #randomly decide to stop at n syllables or extend again
                r = random.randrange(0,100)
                if (r > 100 - (100**(1/3))**pos):
                    #end the name
                    break
                else:
                    #extend another syllable, add set to sets
                    pos += 1
                    sets.append(set)
                    set = []
            #a syllable
            else:
                #if the length of the syllable is more than one letter, add it to the set
                #not neccesary, but I think it makes the names look nicer
                if len(line.strip()) > 1:
                    set.append(line.strip())
                pass

    #construct the name
    result = ""
    for set in sets:
        #pick a random syllable from each set of syllables 
        result += set[random.randint(0,len(set)-1)]
    return result

#make a name and print it
def main():
    print(makeName() + " " + getLastName())


def getLastName(culture):
    '''gets a random last name'''
    #opens the surname file and takes one at random
    cultureFolderPath = generatePath(culture)
    with open(cultureFolderPath + "surnames.txt") as f:
        names = f.readlines()
        name = names[random.randint(0,len(names)-1)].strip()
        name = name.capitalize()
        return name

def getPlaceName(culture):
    cityBits = []
    cultureFolderPath = generatePath(culture)
    with open(cultureFolderPath + "placeNamePatterns.txt") as f:
        patterns = f.readlines()
        pattern = patterns[random.randint(0,len(patterns)-1)].strip()
        pattern = pattern.format(NAME=makeName(culture))
        return pattern

def testNames(culture,iterations):
    for x in range(iterations):
        first = makeName(culture)
        last = getLastName(culture)
        #location = "ipanema"
        location = getPlaceName(culture)
        print("{first} {last} from {location}".format(first=first,last=last,location=location))


if __name__ == "__main__":
    testNames(CONST.cultures.LIBERTARIAD,10)