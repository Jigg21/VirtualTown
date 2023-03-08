import random
import math

#generate a name from the nameGen.txt file
def makeName():
    sets = []
    #open the syllable file 
    with open("data/Cultures/Nomadic/nameGen.txt") as f:
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


def getLastName():
    '''gets a random last name'''
    #opens the surname file and takes one at random
    with open("data/Cultures/Nomadic/surnames.txt") as f:
        name = f.readlines()[random.randint(0,20000)].strip()
        name = name.capitalize()
        return name

def getPlaceName():
    cityBits = []
    
    with open("cities.txt",encoding="UTF-8") as f:
        for line in f.readlines():
            line.strip()
            for bit in line.split(" "):
                cityBits.append(bit)
    result = ""
    for i in range(random.randrange(1,4)):
        result += cityBits[random.randrange(0,len(cityBits))]
    return result

if __name__ == "__main__":
    for x in range(10):
        print(getPlaceName())
