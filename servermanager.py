from subprocess import Popen, PIPE
from enum import Enum
import os

class ServerManager:
    def __init__(self, serverSettings):
        java = serverSettings["javaPath"]
        jarPath = serverSettings["serverPath"]
        dirPath = os.path.dirname(jarPath)
        self.__subprocess = None
        self.__serverstate = ServerState.DOWN
        
        minRAM = "-Xms" + str(serverSettings["minRAM"]) + "G"
        maxRAM = "-Xmx" + str(serverSettings["maxRAM"]) + "G"

        self.__serverargs = [java, minRAM, maxRAM, "-jar", jarPath]

    def getState(self):
        return self.__serverstate

    #start the paper server
    async def openServer(self):
        self.__serverstate = ServerState.PROCESSING
        self.__subprocess = Popen(self.__serverargs, stdout=PIPE, stdin=PIPE, cwd=self.__dirPath)
        
        reader = self.__subprocess.stdout
        nextline = ""
        while nextline.find("Done") == -1:
            nextline = reader.readline().decode("utf-8")

        self.__serverstate = ServerState.RUNNING

    #close the paper server
    async def closeServer(self):
        self.__serverstate = ServerState.PROCESSING
        reader = self.__subprocess.stdout

        self.__subprocess.communicate(input="stop\n")
        nextline = ""
        while nextline.find("Closing Server") == -1:
            nextline = reader.readline().decode("utf-8")

    #force the exit of the server
    def forcekill(self):
        self.__subprocess.kill()
        self.__serverstate = ServerState.KILLED


#State used to convey what the server is doing right now
#Will be used to stop users from starting the server multiple times in a row, etc
class ServerState(Enum):
    RUNNING = 2
    PROCESSING = 1
    DOWN = 0
    KILLED = -1
