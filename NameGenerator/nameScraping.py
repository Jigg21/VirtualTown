from uuid import NAMESPACE_URL
from nltk.tokenize import LegalitySyllableTokenizer
from nltk.corpus import words
import re

class NameScraper():
    '''a class to scrape the names.txt file into syllables'''
    def __init__(self) -> None:
        self.lists = []

    def scrapeSyllables(self,file):
        '''scrapes the data/names.txt file for syllables'''
        #open names
        names = list()
        with open(file) as f:
            names = f.readlines()
        
        #use legality principle tokenizer to split names into syllables
        LP = LegalitySyllableTokenizer(words.words())
        for name in names:
            name = name.strip()
            syls = LP.tokenize(name)
            #pack the syllables into the syllable list   
            self.pack(*syls)
        

    def pack(self,*syls):
        '''takes sylables and inserts them into the syllable list'''
        #extend the syllable list if more syllables are needed
        if len(syls) > len(self.lists):
            while len(syls) > len(self.lists):
                self.lists.append([])
        #put the sylables into the list in the same position as they are in the name
        for i in range(len(syls)):
            self.lists[i].append(syls[i])
    
    #print the syllable list
    def display(self):
        for syls in self.lists:
            for syl in syls:
                print(syl)
    
    #output the syllable list into a file
    def output(self,output):
        with open(output, "w") as f:
            for pos in range(len(self.lists)):
                f.write("$Len{pos}\n".format(pos=pos))
                for i in range(len(self.lists[pos])):
                    f.write(self.lists[pos][i])
                    f.write("\n")

#Scrape and output the result to nameGen.txt
def main():
    #NS = NameScraper()
    #NS.scrapeSyllables("data/names.txt")
    #NS.output("data/nameGen.txt")

    regexTerminal("input.txt")
    return
    cityScraping = NameScraper()
    cityScraping.scrapeSyllables("../data/cities.txt")
    cityScraping.output("../data/cityGen.txt")

def removeNumeric(file,thresh=0):
    '''remove lines that are purely numeric,
    specify thresh to determine which %  can be alpha and still be removed '''
    goodValues = []
    with open(file,"r") as f:
        #for each line in the file
        for line in f.readlines():
            line.strip()
            #if the line has letters in it
            if not line.isnumeric():
                #make sure the line is at least thresh% letters
                numPer = 0
                for letter in line:
                    if letter.isnumeric():
                        numPer += 1
                #if the line is over the threshold
                if numPer/len(line) <= thresh:
                    goodValues.append(line)
            else:
                goodValues.append(line)
    with open(file,"w") as w:
        for line in goodValues:
            w.write(line)

def removeUnencodable(file):
    '''remove any line in the file that can't be read'''
    goodValues = []
    with open(file,"r") as f:
        for i in range(0,10000):
            try:
                goodValues.append(f.readline())
            except:
                print("bad encode")
    with open(file,"w") as w:
        for line in goodValues:
            w.write(line)

def regexTerminal(file):
    with open(file,"r") as f:
        cmd = ""
        fileList = f.readlines()
        fileString = ""
        for line in fileList:
            fileString += line + "\n"
        while cmd != "quit":
            cmd = input("enter regex pattern")
            search = re.compile(cmd)
            results = search.findall(fileString)
            print("{match} results found!".format(match=len(results)))
            if len(results) > 0:
                cmd = input("What command?")
                if cmd == "del":
                    for line in fileList:
                        if search.match():
                            pass



if __name__ == "__main__":
    NS = NameScraper()
    NS.scrapeSyllables("input.txt")
    NS.output("output.txt")
    




