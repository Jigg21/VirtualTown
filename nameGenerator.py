import random
import math

#generate a name from the nameGen.txt file
def makeName():
    sets = []
    with open("data/nameGen.txt") as f:
        sets = []
        set = []
        pos = 0
        #write in lines until it reaches a syllable boundary
        for line in f.readlines():
            #reached a boundary
            if line[0] == "$":
                r = random.randrange(0,100)
                if (r > 100 - (100**(1/3))**pos):
                    #end the name
                    break
                else:
                    #extend another syllable, add set to sets
                    pos += 1
                    sets.append(set)
                    set = []
            else:
                #if the length of the syllable is more than one letter, add it to the set
                if len(line.strip()) > 1:
                    set.append(line.strip())
                pass

    #construct the name
    result = ""
    for set in sets:
        if len(set) > 1:
            result += set[random.randint(0,len(set)-1)]
    return result

#make a name and print it
def main():
    print(makeName() + " " + getLastName())

def getLastName():
    with open("data/surnames.txt") as f:
        name = f.readlines()[random.randint(0,20000)].strip()
        name = name.capitalize()
        return name

if __name__ == "__main__":
    for x in range(10):
        main()
