from enum import Enum
import csv
RECIPES = None

def loadRecipeData():
    global RECIPES
    if RECIPES != None:
        return RECIPES
    else:
        RECIPES = {}
        with open('data\\Recipes.csv') as csvFile:
                reader = csv.DictReader(csvFile)
                for row in reader:
                    RECIPES[row["Name"]] = row
    return RECIPES

print(loadRecipeData())