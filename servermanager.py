from subprocess import Popen, PIPE
from enum import Enum
import os

class ServerManager:
    def __init__(self, jarPath, javapath = "/usr/bin/java", minRAM="-Xms2G", maxRAM="-XMS8G"):
        self.__java = javapath
        self.__jarPath = jarPath 
        self.__dirPath = os.path.dirname(jarPath)
        self.__subprocess = None
        self.__serverstate = ServerState.DOWN
        self.__serverargs = [javapath, minRAM, maxRAM, "-jar", jarPath]

    def getState(self):
        return self.__serverstate

    async def openServer(self):
        self.__serverstate = ServerState.PROCESSING
        self.__subprocess = Popen(self.__serverargs, stdout=PIPE, stdin=PIPE, cwd=self.__dirPath)
        
        reader = self.__subprocess.stdout
        nextline = ""
        while nextline.find("Done") == -1:
            nextline = reader.readline().decode("utf-8")

        self.__serverstate = ServerState.RUNNING

    async def closeServer(self):
        self.__serverstate = ServerState.PROCESSING
        reader = self.__subprocess.stdout

        self.__subprocess.communicate(input="stop\n")
        nextline = ""
        while nextline.find("Closing Server") == -1:
            nextline = reader.readline().decode("utf-8")

    def forcekill(self):
        self.__subprocess.kill()
        self.__serverstate = ServerState.DOWN


class ServerState(Enum):
    RUNNING = 1
    PROCESSING = 0
    DOWN = -1
