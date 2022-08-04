from uuid import NAMESPACE_URL
from nltk.tokenize import LegalitySyllableTokenizer
from nltk.corpus import words

class NameScraper():

    def __init__(self) -> None:
        self.lists = []

    def scrapeFirstNameSyllables(self):
        names = list()
        with open("data/names.txt") as f:
            names = f.readlines()
        
        LP = LegalitySyllableTokenizer(words.words())
        for name in names:
            name = name.strip()
            syls = LP.tokenize(name)   
            self.pack(*syls)
        

    def pack(self,*syls):
        if len(syls) > len(self.lists):
            while len(syls) > len(self.lists):
                self.lists.append([])
        for i in range(len(syls)):
            self.lists[i].append(syls[i])
    
    def display(self):
        for syls in self.lists:
            for syl in syls:
                print(syl)
    
    def output(self):
        with open("data/nameGen.txt", "w") as f:
            for pos in range(len(self.lists)):
                f.write("$Len{pos}\n".format(pos=pos))
                for i in range(len(self.lists[pos])):
                    f.write(self.lists[pos][i])
                    f.write("\n")

        


def main():
    NS = NameScraper()
    NS.scrapeFirstNameSyllables()
    NS.output()

if __name__ == "__main__":
    main()


