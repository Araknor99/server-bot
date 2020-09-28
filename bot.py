import discord
from logger import Logger
from servermanager import ServerManager, ServerState
import os
import sys

class serverClient(discord.Client):
    def __init__(self,argv=[]):
        super.__init__()
        self.javaPath = "usr/bin/java"
        self.serverPath = "./server/paper.jar"
        self.minRam = 2
        self.maxRam = 8
        self.logPath = "log.txt"
        self.__standardChannel = ""
        
        self.interpretArgs(argv)

        self.__servermanager = ServerManager(serverPath,javaPath,minRAM,maxRAM)
        self.__logger = Logger(logPath)

    def interpretArgs(self,argv):
        for i in range(len(argv)):
            arg = argv[i]
            if arg[:2] == "--":
                try:
                    value = argv[i+1]
                    if value[:2] == "--":
                        raise IndexError
                except IndexError:
                    print("No value for flag " + arg + ".\nExiting...")
                    sys.exit()

        for i in range(len(argv)):
            arg = argv[i][1:]
            value = argv[i+1]
            
            if arg == "javaPath":
                self.javaPath == value
            elif arg == "serverPath":
                self.serverPath == value
            elif arg == "minRAM":
                self.minRAM = int(value)
            elif arg == "maxRAM":
                self.maxRAM = int(value)
            elif arg == "logPath":
                self.maxRAM = value
            elif arg == "standardChannel":
                self.__standardChannel = arg
            else:
                print("Unknown variable \"" + value + "\"!\nExiting...")

    async def on_ready(self):
        pass

    async def on_message(self, message):
        pass

def getToken(path):
    file = open(path,"r")
    token = file.readline()
    file.close()
    return token


if __name__== "__main__":
    client = serverClient()
    client.run(getToken(TOKENPATH))