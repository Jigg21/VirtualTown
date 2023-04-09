import random
import os
import sys
root_folder = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_folder)

import CONST

def generatePath(culture):
    cultureFile = root_folder+"/data/Cultures/"
    if culture == CONST.cultures.ROMAN:
        cultureFile += "Roman/"
    if culture == CONST.cultures.NOMAD:
        cultureFile += "Nomadic/"
    if culture == CONST.cultures.LIBERTARIAD:
        cultureFile += "Libertariad/"
    return cultureFile 

#generate a name from the nameGen.txt file
def makeName(culture):
    '''Generate a name as a mix of syllables dictated by the culture dict provided'''
    #if the supplied culture is a basic constant, construct a simple culture and pass it
    if type(culture) == CONST.cultures:
        simpleCulture = dict()
        for c in CONST.cultures:
            simpleCulture[c] = 0
        simpleCulture[culture] = 1
        culture = simpleCulture

    majorCulture = CONST.cultures.NOMAD
    majorCultureVal = 0

    length = 0
    r = random.randrange(0,100)
    name = ""
    while (r < 100 - (100**(1/3))**length):
        keys = list(culture.keys())
        values = list(culture.values())        
        minorCulture = random.choices(keys,values)[0]
        
        #open the chosen minor culture file
        cultureFolderPath = generatePath(minorCulture)
        with open(cultureFolderPath+"nameGen.txt") as f:
            #write in lines until you find the one 
            lineNum = 0
            lines = f.readlines()
            try:
                options = lines[length].split(",")
                name += random.choice(options).strip()
            except Exception() as e:
                print(e)
        
        r = random.randrange(0,100)
        length += 1
    return name

#make a name and print it
def main():
    print(makeName() + " " + getLastName())


def getLastName(culture):
    '''gets a random last name from the culture data files'''
    #opens the surname file and takes one at random
    cultureFolderPath = generatePath(culture)
    with open(cultureFolderPath + "surnames.txt") as f:
        names = f.readlines()
        name = names[random.randint(0,len(names)-1)].strip()
        name = name.capitalize()
        return name

def getNoun(culture):
    '''gets a random noun from the culture data file'''
    cultureFolderPath = generatePath(culture)
    with open(cultureFolderPath + "nouns.txt") as f:
        nouns = f.readlines()
        noun = nouns[random.randint(0,len(nouns)-1)].strip()
        noun = noun.capitalize()
        return noun

def getPlaceName(culture):
    '''constructs a location name'''
    cityBits = []
    cultureFolderPath = generatePath(culture)
    with open(cultureFolderPath + "placeNamePatterns.txt") as f:
        patterns = f.readlines()
        pattern = patterns[random.randint(0,len(patterns)-1)].strip()
        #sub in values
        if "{NAME}" in pattern:
            pattern = pattern.format(NAME=makeName(culture))
        if "{NOUN}" in pattern:
            pattern = pattern.format(NOUN=getNoun(culture))
        return pattern

def getMajorCulture(culture):
    majorCulture = CONST.cultures.NOMAD
    majorCultureVal = 0
    for minorCulture in culture:
        if culture[minorCulture] > majorCultureVal:
            majorCulture = minorCulture
            majorCultureVal = culture[minorCulture]
    return majorCulture


def testNames(culture,iterations):
    '''creates iterations number of person and location names'''
    majorCulture = getMajorCulture(culture)
    for x in range(iterations):
        first = makeName(culture)
        last = getLastName(majorCulture)
        location = getPlaceName(majorCulture)
        print("{first} {last} from {location}".format(first=first,last=last,location=location))


if __name__ == "__main__":            
    testCulture = dict()
    testCulture[CONST.cultures.NOMAD] =  0
    testCulture[CONST.cultures.LIBERTARIAD] = .5
    testCulture[CONST.cultures.ROMAN] = .5
    testNames(testCulture,10)