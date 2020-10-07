from subprocess import Popen, PIPE
from enum import Enum
import os

class ServerManager:
    def __init__(self):
        self.__subprocess = None
        self.__state = ServerState.DOWN
        self.__serverargs = None
        self.onServerStarted = None
        self.onServerClosed = None

    def getState(self):
        return self.__state

    def setArgs(self,settings):
        if self.__server.isOperating():
            return False

        self.__settings = settings
        minRAM = "-Xms" + str(settings["minRAM"]) + "G"
        maxRAM = "-Xmx" + str(settings["maxRAM"]) + "G"
        
        args = [settings["javaPath"],minRAM,maxRAM,"-jar",settings["serverPath"]]
        self.__server.setArgs(args)
        return True

    #start the paper server
    def openServer(self):
        if self.isRunning() or self.isProcessing():
            return False

        self.__state = ServerState.PROCESSING
        self.__subprocess = Popen(self.__serverargs, stdout=PIPE, stdin=PIPE, cwd=self.__dirPath)
        
        reader = self.__subprocess.stdout
        nextline = ""
        while nextline.find("Done") == -1:
            nextline = reader.readline().decode("utf-8")

        self.__state = ServerState.RUNNING
        return True

    #close the paper server
    def closeServer(self):
        if self.isDown() or self.isProcessing():
            return False

        self.__state = ServerState.PROCESSING
        reader = self.__subprocess.stdout

        self.__subprocess.communicate(input="stop\n")
        nextline = ""
        while nextline.find("Closing Server") == -1:
            nextline = reader.readline().decode("utf-8")

        self.__state = ServerState.DOWN
        return True

    #force the exit of the server
    def forcekill(self):
        self.__subprocess.kill()
        self.__state = ServerState.KILLED


    #Three functions which have the sole purpose of improving the code readibility
    def isRunning(self):
        if self.state > 1:
            return True
        return False

    def isProcessing(self):
        if self.__state == ServerState.PROCESSING:
            return True
        return False

    def isDown(self):
        if self.state < 1:
            return True
        return False


#State used to convey what the server is doing right now
#Will be used to stop users from starting the server multiple times in a row, etc
class ServerState(Enum):
    RUNNING = 2
    PROCESSING = 1
    DOWN = 0
    KILLED = -1
