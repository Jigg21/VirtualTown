import random

def makeName():
    sets = []
    with open("data/nameGen.txt") as f:
        sets = []
        set = []
        pos = 1
        for line in f.readlines():
            if line[0] == "$":
                r = random.randrange(0,100)
                if (r > 100/pos):
                    break
                else:
                    pos += 1
                    sets.append(set)
                    set = []
            else:
                if len(line.strip()) > 0:
                    set.append(line.strip())
                pass


    result = ""
    while len(result) < 2:
        for set in sets:
            if len(set) > 1:
                result += set[random.randint(0,len(set)-1)]
    return result

def main():
    print(makeName())

if __name__ == "__main__":
    main()
