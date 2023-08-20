from Town import Ship
import sys
from WorldGen import WorldGenerator

def main():
    print("Starting TerraGen!")


def generateWorld():
    WorldGenerator.WorldObj()


if __name__ == "__main__":
    for arg in sys.argv:
        if arg == "-w":
            print("Generating World")
            generateWorld()
            break
    main()