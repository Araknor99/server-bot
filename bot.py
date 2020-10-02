#!/usr/bin/python3
import discord
from logger import Logger
from servermanager import ServerManager, ServerState
import os
import sys

TOKENPATH = "token.secret"

#Sadly, I cannot use the __init__() of the class
class serverClient(discord.Client):
    def onReadyInit(self,argv=[]):
        self.javaPath = "usr/bin/java"
        self.serverPath = "./server/paper.jar"
        self.minRAM = 2
        self.maxRAM = 8
        self.logPath = "log.txt"
        self.__standardChannel = ""
        
        self.interpretArgs(argv)

        self.__servermanager = ServerManager(self.serverPath,self.javaPath,self.minRAM,self.maxRAM)
        self.__logger = Logger(self.logPath,True)

        #There has to be a better way
        self.__logger.writeToLog("Using java path: " + self.javaPath)
        self.__logger.writeToLog("Using following path for paper.jar: " + self.serverPath)
        self.__logger.writeToLog("Minimial RAM usage: " + str(self.minRAM) + " Gigabytes")
        self.__logger.writeToLog("Maximial RAM usage: " + str(self.maxRAM) + " Gigabytes")
        self.__logger.writeToLog("Using path for log file: " + self.logPath)

        self.getCurrentChannel()
        
        self.__ready = True
        self.__logger.writeToLog("Ready!")

    def interpretArgs(self,argv):
        for i in range(0,len(argv),2):
            arg = argv[i]
            if arg[:2] == "--":
                try:
                    if i+1 > len(argv):
                        raise IndexError
                    value = argv[i+1]
                    if value[:2] == "--":
                        raise IndexError
                except IndexError:
                    print("No value for flag " + arg + ".\nExiting...")
                    sys.exit()
            else:
                print("No flag supplied for value: " + arg + ".\nExiting...")
                sys.exit()

        for i in range(0,len(argv),2):
            arg = argv[i][2:]
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
                self.logPath = value
            elif arg == "standardChannel":
                self.__standardChannel = arg
            else:
                print("Unknown flag \"" + arg + "\"!\nExiting...")

    def getCurrentChannel(self):
        pass


    #actual message handling and so on
    async def on_ready(self):
        print("Warming up the utilities!")
        self.__ready = False
        self.onReadyInit(sys.argv[1:])

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