import socket
import select
from threading import Thread
from threading import Event
from enum import Enum
class Responses(Enum):
    COMPLETE = 0
    WAITING = 1
    TIMEOUT = 2

#TODO: Add encryption and authentication
class ShipNetworkAdapter():
    def __init__(self,shipObj) -> None:
        '''How a ship communicates with a server '''
        self.sock = socket.socket()
        self.port = 12925
        self.sock.connect(('127.0.0.1',self.port))
        self.ship = shipObj
    
    def __del__(self):
        #deconstructor
        self.sock.close()

    def getCurrentTime(self):
        '''get the current time in cycles from the server'''
        self.sock.send(b"REQ_CURRENTTIME")
        receive = self.sock.recv(16)
        receive = int(receive.decode())
    
    def connect(self):
        '''join the servers main loop until interupted'''
        try:
            print("Joining the Server loop now")
            while True:
                ready = select.select([self.sock],[],[],1)
                if ready[0]:
                    message = self.sock.recv(16)
                    #update when the server commands it
                    if message == b"CMD_UPDATE":
                        Stop = Event()
                        newShipState = []
                        update = shipUpdate(Stop,self.ship,newShipState)
                        update.start()
                        update.join(.8)
                        if update.is_alive():
                            print("TOOK TOO LONG!")
                            self.sock.send(b"ACK_TIMEREQ")
                            Stop.set()
                            update.join()
                        else:
                            self.sock.send(b"ACK_COMPLETE")
                            print("COMPLETED!")
                else:
                    pass
        except KeyboardInterrupt:
            pass

class shipUpdate(Thread):
    StopEvent = 0

    def __init__(self,args,ship,output) -> None:
        super().__init__(daemon=True)
        self.StopEvent = args
        self.ship = ship
        self.output = output
    
    def run(self):
        #TODO:Attach to ship update
        if (self.StopEvent.wait(0)):
            print("Stopping")
            return
        self.output.append(self.ship.timeUpdate())
        print("exiting!")
