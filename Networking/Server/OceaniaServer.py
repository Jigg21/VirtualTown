import socket
import select
import logging
import threading
import time
from enum import Enum

logging.basicConfig(filename="ServerLog.log",level=logging.INFO)

class NetworkResponses(Enum):
    COMPLETE = 0
    WAITING = 1
    TIMEOUT = 2

class OceaniaServer():
    '''server to coordinate various ship instances'''
    def __init__(self) -> None:
        #ship objects
        self.ships = []
        #current in-sim cycle
        self.currentCycle = 0
        #initialize and setup a socket for communication
        self.sock = socket.socket()
        #self.sock.setblocking(0)
        port = 12925
        logging.info("Server socket created")
        self.sock.bind(('',port))
        logging.info("Socket bound to {port}".format(port=port))
        self.sock.listen(5)
        print("Server Listening!")
        logging.info("Socket open...")
        self.animation = "|/-\\"
        self.animationIdx = 0
    
    def launch(self):
        '''update each ship and wait for responses'''
        try:
            while True:
                startTime = time.time()
                print("Starting Cycle {cycle}".format(cycle=self.currentCycle))
                if len(self.ships) == 0:
                    print("NO ONE! Waiting for new ship...")
                    self.acceptNewShips()
                #TODO: add multithreading
                purgeShips = []
                for ship in self.ships:
                    result = ship.update()
                    if result == NetworkResponses.TIMEOUT:
                        purgeShips.append(ship)
                
                for ship in purgeShips:
                    self.ships.remove(ship)
                time.sleep(1-(time.time()-startTime))
                self.currentCycle += 1
        except Exception as e:
            print(e)

    def acceptNewShips(self):
        connection, addr = self.sock.accept()
        logging.info("New ship connected from {addr}!".format(addr=addr))
        print("{addr} connected!".format(addr=addr))
        self.ships.append(ShipClient(connection,addr))

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
            print("Client Exception: ",e)
        
def main():
    server = OceaniaServer()
    server.acceptNewShips()
    while True:
        server.launch()




if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Server stopped by keyboard, Goodbye!")
    