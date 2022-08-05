from uuid import NAMESPACE_URL
from nltk.tokenize import LegalitySyllableTokenizer
from nltk.corpus import words


class NameScraper():
    '''a class to scrape the names.txt file into syllables'''
    def __init__(self) -> None:
        self.lists = []

    def scrapeSyllables(self):
        '''scrapes the data/names.txt file for syllables'''
        #open names
        names = list()
        with open("data/names.txt") as f:
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
    def output(self):
        with open("data/nameGen.txt", "w") as f:
            for pos in range(len(self.lists)):
                f.write("$Len{pos}\n".format(pos=pos))
                for i in range(len(self.lists[pos])):
                    f.write(self.lists[pos][i])
                    f.write("\n")

#Scrape and output the result to nameGen.txt
def main():
    NS = NameScraper()
    NS.scrapeSyllables()
    NS.output()

if __name__ == "__main__":
    main()


