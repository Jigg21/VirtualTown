import socket
import select
import logging
from threading import Thread
from threading import Event
import time
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import traceback

logging.basicConfig(filename="ServerLog.log",level=logging.INFO)

class NetworkResponses(Enum):
    COMPLETE = 0
    WAITING = 1
    TIMEOUT = 2

class GenTerraServer():
    '''server to coordinate various ship instances'''
    def __init__(self) -> None:
        #ship objects
        self.ships = []
        self.newShips = []
        self.purgeShips = []
        #current in-sim cycle
        self.currentCycle = 0
        
        self.animation = "|/-\\"
        self.animationIdx = 0
    
    def launch(self):
        '''launch the server '''
        try:
            #start the 
            Stop = Event()
            newConnections = acceptNewConnections(Stop,self.newShips)
            newConnections.start()
            with ThreadPoolExecutor(max_workers=5) as executor:
                while True:
                    #get the start time of this cycle
                    startTime = time.time()

                    #if there are new connections, add them to the ship list and restart the joining thread
                    if not newConnections.is_alive():
                        newConnections.join()
                        newConnections.sock.close()
                        for ship in self.newShips:
                            self.acceptNewShip(ship)
                        self.newShips = list()
                        newConnections = acceptNewConnections(Stop,self.newShips)
                        newConnections.start()
                    
                    #perform any pre update functions before starting
                    self.preExecution()
                    #start the next cycle if there is at least one ship
                    if len(self.ships) == 0:
                        print("NO ONE! Waiting for new ship...")
                    else:
                        print("Starting Cycle {cycle}".format(cycle=self.currentCycle))
                        #start the threads 
                        ShipFutures = dict()
                        for ship in self.ships:
                            ShipFutures[ship] = executor.submit(ship.update)
                        #wait some time
                        time.sleep(.75)
                        #proccess responses
                        for future in ShipFutures.keys():
                            #reject the ships that are not responding
                            if not ShipFutures[future].done():
                                self.purgeShips.append(future)
                            else:
                                #reject the timeouts
                                result = ShipFutures[future].result()
                                if result == NetworkResponses.TIMEOUT:
                                    self.purgeShips.append(future)
                                #for the ships that completed successfully
                                elif result == NetworkResponses.COMPLETE:
                                    pass
                                #for the ships that need more time
                                elif result == NetworkResponses.WAITING:
                                    pass
                        self.postExecution()
                    time.sleep(1-(time.time()-startTime))        
        except Exception:
            print(traceback.format_exc())

    def preExecution(self):
        '''
        actions that happen before update execution
            
        '''
        pass

    def postExecution(self):
        '''actions that happen after ships have updated'''
        for ship in self.purgeShips:
            self.ships.remove(ship)
        self.purgeShips = []
        self.currentCycle += 1
        pass
    
    def acceptNewShip(self,otherShip):
        '''actions that execute when a ship joins the fold'''
        self.ships.append(otherShip)

class acceptNewConnections(Thread):
    def __init__(self,stop,shipList) -> None:
        super().__init__(daemon=True)
        self.StopEvent = stop
        self.shipList = shipList
        #initialize and setup a socket for communication
        self.sock = socket.socket()
        #self.sock.setblocking(0)
        port = 12925
        logging.info("Server socket created")
        self.sock.bind(('',port))
        logging.info("Socket bound to {port}".format(port=port))
        self.sock.listen(5)
        print("Server Listening!")
        logging.info("Socket opened at {time}".format(time=time.ctime()))
    
    def run(self):
        connection, addr = self.sock.accept()
        logging.info("New ship connected from {addr}!".format(addr=addr))
        print("{addr} connected!".format(addr=addr))
        self.shipList.append(ShipClient(connection,addr))

class ShipClient():
    def __init__(self,socket,addr):
        self.conn = socket
        self.ready = False
        self.addr = addr
    
    def update(self):
        '''sends an update and expects a response'''
        try:
            #sends the update command
            self.conn.send(b"CMD_UPDATE")
            #wait up to .8 seconds for a response 
            response = select.select([self.conn],[],[],.8)
            if response[0]:
                data = self.conn.recv(16)
                print("received Response:", data)
                return NetworkResponses.COMPLETE
            else:
                logging.info("Client {addr} timed out!".format(addr=self.addr))
                return NetworkResponses.TIMEOUT
        except WindowsError as e:
                    if e.winerror == 10053:
                        logging.info("Client {addr} timed out!".format(addr=self.addr))
                        return NetworkResponses.TIMEOUT
        except Exception as e:
            print("Exception in Client Update: ",e)
        
def main():
    server = GenTerraServer()
    server.launch()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Server stopped by keyboard, Goodbye!")
    