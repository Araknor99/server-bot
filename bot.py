#!/usr/bin/python3
import discord
import asyncio
from logger import Logger
from servermanager import ServerManager, ServerState
from settings import SettingsManager
import os
import sys

TOKENPATH = "token.secret"

#Sadly, I cannot use the __init__() of the class
class serverClient(discord.Client):
    #--------------------------------------------
    #| Functions mostly used for initialization |
    #--------------------------------------------
    async def onReadyInit(self,argv=[]):
        self.__settingsManager = SettingsManager()
        self.__settings = self.__settingsManager.getSettings()
        self.__serverSettings = self.__settings["serverSettings"]

        if not await self.interpretArgs(argv):
            await self.close()
            return

        if self.__serverSettings["minRAM"] > self.__serverSettings["maxRAM"]:
            print("Setting minRAM cannot be bigger than maxRAM!\nExiting...")
            await self.close()
            return

        self.__servermanager = ServerManager(self.__settings["serverSettings"])
        self.__logger = Logger(self.__settings["logPath"],True)

        if self.__settingsManager.onDefaultSettings():
            self.__logger.writeToLog("No custom settings set! Running on default settings!")

        #There has to be a better way
        serverSettings = self.__settings["serverSettings"]
        self.__logger.writeToLog("Using java path: " + serverSettings["javaPath"])
        self.__logger.writeToLog("Using following path for paper.jar: " + serverSettings["serverPath"])
        self.__logger.writeToLog("Minimial RAM usage: " + str(serverSettings["minRAM"]) + " Gigabytes")
        self.__logger.writeToLog("Maximial RAM usage: " + str(serverSettings["maxRAM"]) + " Gigabytes")
        self.__logger.writeToLog("Using path for log file: " + self.__settings["logPath"])

        if(self.__settings["standardChannel"] == ""):
            self.__logger.writeToLog("No standard channel has been set! Exiting the bot!")
            self.__logger.endLog()
            await self.close()
            return
        
        self.__ready = True
        self.__logger.writeToLog("Ready!")

    async def interpretArgs(self,argv):
        #Check whether the flags have been set correctly
        #Might change functionality to support flags that need no value set
        #If the function cannot interpret the arguments then it returns False
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
                    return False
            else:
                print("No flag supplied for value: " + arg + ".\nExiting...")
                return False

        #Actually set the values
        for i in range(0,len(argv),2):
            arg = argv[i][2:]
            value = argv[i+1]
            
            #return False if the option does not exist so we can close the bot
            if not self.setOption(arg,value,self.__settings):
                print("Option '" + arg + "' does not exist!")
                return False
        return True

    def setOption(self,option,value,dictionairy):
        for key,setting in dictionairy.items():
            if isinstance(setting,dict):
                return self.setOption(option,value,dictionairy[key])
            if key == option:
                if isinstance(setting,int):
                    value = int(value)
                dictionairy[key] = value
                return True
        return False

    #-----------------------------------------------
    #| These functions do all the actual bot stuff |
    #-----------------------------------------------
    def checkMessage(self, message: discord.Message):
        pass

    async def on_ready(self):
        print("Warming up the utilities!")
        self.__ready = False
        await self.onReadyInit(sys.argv[1:])

    async def on_message(self, message):
        pass

#Get bot token
def getToken(path):
    file = open(path,"r")
    token = file.readline()
    file.close()
    return token

#start the bot
if __name__== "__main__":
    client = serverClient()
    client.run(getToken(TOKENPATH))