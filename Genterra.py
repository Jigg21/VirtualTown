from TownInterface import RenderInterface
from Utilities.ConfigReader import ConfigData as config
from Town import CaptainsLog
from Town import Town
import sys
import time
from TownInterface import interface as UI
import traceback
import signal
import threading



def main(args):
    command = args[1]
    if command == "renderPlanet":
        print("Doing My Best!")
        RenderInterface.Renderer().initialize()
    elif command == "play":
        #test = weatherGenerator.weatherManager()
        #print(test.getDayLightHours())
        #return 
        online = config.getboolean("NETWORKING","ONLINE")
        #initialize a test ship
        testTown = Town.Ship("New New New York",online=online)

        #if just speedtesting, get average speed over TESTCOUNT ticks
        if config.getboolean("DEBUG","SPEEDTEST"):
            time_start = time.time()
            for x in range(config.getint("DEBUG","TESTCOUNT")):
                testTown.timeUpdate()
            time_end = time.time()
            print("Average Time was {number}".format(number = (time_end-time_start)/config.getint("DEBUG","TESTCOUNT")))
            CaptainsLog.closeLogs()
            input("Close")
            return
        

        #CENTRAL FINITE CURVE
        if online:
            #if the ship is online, online behaviors are needed
            testTown.connect()
        else:
            try:
                #start the offline update thread
                pauseEvent = threading.Event()
                sim = Town.OfflineUpdate(testTown,pauseEvent)
                sim.start()
                if config.getboolean("VALUES","USEUI"):
                    shipUI = UI.ShipWindow()
                    shipUI.inititialize(testTown.townName,testTown.context,pauseEvent)
            except Exception as e:
                print("====EXITING===")
                print(str(e))
                print(traceback.format_exc())
                testTown.displayLocalTime()
                signal.raise_signal(signal.SIGTERM)
                sim.join()
                
    
                #de-initialize

                CaptainsLog.closeLogs()
                if config.getboolean("DEBUG","INSTANT"):
                    input("Close")
        
            return

if __name__ == "__main__":
    args = sys.argv
    main(args)