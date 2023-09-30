from TownInterface import RenderInterface
from Utilities.ConfigReader import ConfigData as config
from Town import CaptainsLog
from Town import Town
import time
from TownInterface import interface as UI
import traceback
import signal
import threading
import argparse


def main(args):
    if args.render:
        print("Doing My Best!")
        RenderInterface.Renderer().initialize()
    else:

        #test = weatherGenerator.weatherManager()
        #print(test.getDayLightHours())
        #return 
        online = args.online
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
    parser = argparse.ArgumentParser(description='Genterra parsing',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-o","--online",action="store_true",help="online mode")
    parser.add_argument("-t","--terminal",action="store_true",help="terminal mode, no graphics")
    parser.add_argument("-s","--server",action="store_true",help="server mode")
    parser.add_argument("-r","--render",action="store_true",help="render a planet")




    args = parser.parse_args()
    main(args)