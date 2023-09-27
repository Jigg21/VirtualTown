from TownInterface import RenderInterface
import Town
import sys

def main(args):
    print(args)
    command = args[1]
    if command == "renderPlanet":
        RenderInterface.Renderer().initialize()
    elif command == "play":
        Town.main()

if __name__ == "__main__":
    args = sys.argv
    main(args)