from subprocess import Popen, PIPE
from enum import IntEnum
from pathlib import Path
import os

class ServerManager:
    def __init__(self):
        self.__subprocess = None
        self.__state: IntEnum = ServerState.DOWN
        self.__serverargs = None
        self.__dirPath = None
        self.onServerStarted = None
        self.onServerClosed = None

    def setArgs(self,settings) -> bool:
        minRAM = "-Xms" + str(settings["minRAM"]) + "G"
        maxRAM = "-Xmx" + str(settings["maxRAM"]) + "G"
        self.__dirPath = Path(settings["serverPath"]).parent
        
        self.__serverargs = [settings["javaPath"],minRAM,maxRAM,"-jar",settings["serverPath"]]
        return True

    #start the paper server
    def openServer(self) -> bool:
        if self.isRunning() or self.isProcessing():
            return False

        self.__state = ServerState.PROCESSING
        self.__subprocess = Popen(self.__serverargs, stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd=self.__dirPath)
        
        reader = self.__subprocess.stdout
        nextline = ""
        while nextline.find("Timings Reset") == -1:
            nextline = reader.readline().decode("utf-8")

        self.__state = ServerState.RUNNING
        return True

    #close the paper server
    def closeServer(self) -> bool:
        if self.isDown() or self.isProcessing():
            return False

        self.__state = ServerState.PROCESSING
        reader = self.__subprocess.stdout

        self.__subprocess.communicate(bytes("stop\n","utf-8"))
        while not reader.closed:
            pass

        self.__state = ServerState.DOWN
        return True

    def getState(self) -> IntEnum:
        return self.__state

    def getPlayerCount(self) -> int:
        if self.isDown() or self.isProcessing():
            raise RuntimeError("Unable to get players if server is not running!")

        self.__subprocess.stdin.write(bytes("list\n","utf-8"))
        self.__subprocess.stdin.flush()
        output = self.__subprocess.stdout.readline().decode("utf-8")

        parts = output.split(" ")
        print(parts)

        for part in parts:
            try:
                playerCount = int(part)
                return playerCount
            except ValueError:
                continue

    #print message to people on server
    def printMessage(self,message):
        if self.isDown() or self.isProcessing():
            raise RuntimeError("Unable print message if server is not running!")

        self.__subprocess.stdin.write(bytes("say {}\n".format(message),"utf-8"))
        self.__subprocess.stdin.flush()

    #force the exit of the server
    def forcekill(self):
        self.__subprocess.kill()
        self.__state = ServerState.KILLED


    #Three functions which have the sole purpose of improving the code readibility
    def isRunning(self) -> bool:
        if self.__state > 1:
            return True
        return False

    def isProcessing(self) -> bool:
        if self.__state == ServerState.PROCESSING:
            return True
        return False

    def isDown(self) -> bool:
        if self.__state < 1:
            return True
        return False


#State used to convey what the server is doing right now
#Will be used to stop users from starting the server multiple times in a row, etc
class ServerState(IntEnum):
    RUNNING = 2
    PROCESSING = 1
    DOWN = 0
    KILLED = -1
