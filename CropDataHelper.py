import json



def main():
    try:
        with open('CropData.json') as f:
            cropData = json.load(f)
    except:
        cropData = dict()
    
    cropName = input("Crop Name: ")
    cropRipe = input("Crop Ripe Time (in Y:D:H:M): ")
    cropValue = int(input("Harvest Value: "))
    cropHLabor = int(input("Harvest Labor Cost: "))
    cropMLabor = int(input("Maintainance Labor Cost: "))
    cropColor = input("Crop Color in Hexadecimal (#ffffff) form: ")
    print("{cropName}, takes {cropRipe} to produce {cropValue} food, requiring {cropHLabor} labor to harvest and {cropMLabor} labor to grow. It is the color: {color} ".format(cropName=cropName,cropRipe=cropRipe,cropValue=cropValue,cropHLabor=cropHLabor,cropMLabor=cropMLabor,color=cropColor))
    correct = input("Correct? y/n")
    cropData[cropName] = {"cropRipe":cropRipe,"cropValue":cropValue,"cropHLabor":cropHLabor,"cropMLabor":cropMLabor,"cropColor":cropColor}
    if (correct == "y"):
        with open('CropData.json', 'w') as outfile:
            json.dump(cropData, outfile)
    else:
        return

main()