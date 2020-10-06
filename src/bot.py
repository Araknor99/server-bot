#!/usr/bin/python3
import discord
import asyncio
from logger import Logger
from servermanager import ServerManager, ServerState
from filehandling import FileHandler
from settingsManager import SettingsManager
import os
import sys

TOKENPATH = "../token.secret"

#Sadly, I cannot use the __init__() of the class
class serverClient(discord.Client):
    #----------------------------------------------------------
    #| Functions mostly used for initialization and utilities |
    #----------------------------------------------------------
    async def onReadyInit(self,argv=[]):
        self.__fileHandler = FileHandler()
        self.__sManager = SettingsManager()
        self.__sManager.loadSettings(self.__fileHandler)

        if not self.__sManager.interpretArgs(argv):
            await self.close()
            return

        if not self.__sManager.validateSettings():
            await self.close()
            return

        serverSettings = self.__sManager.getServerSettings()
        settings = self.__sManager.getSettings()

        self.__servermanager = ServerManager(serverSettings)
        self.__logger = Logger(settings["logPath"],True)

        self.__sManager.logSettings(self.__logger)
        
        self.__ready = True
        self.__logger.writeToLog("Ready!")

    #Reload the settings so only the server has to be restarted
    #Since ServerState.DOWN and ServerState.KILLED as ints are smaller than 1...
    #TODO: finish function
    def reloadSettings(self):
        if ServerManager.getState() > 0:
            return False
        else:
            pass

    def getToken(self):
        file = open(TOKENPATH)
        text = file.read()
        file.close()
        return text

    #TODO: finish the function.
    #      Needs to be able to start the server and log the settings
    def startServer(self):
        pass

    #-------------------------------------------------------------
    #| These functions do all the user interaction and bot stuff |
    #-------------------------------------------------------------
    #TODO finish this function
    def checkMessage(self, message: discord.Message):
        pass

    async def on_ready(self):
        print("Warming up the utilities!")
        self.__ready = False
        await self.onReadyInit(sys.argv[1:])

    #TODO finish this function
    async def on_message(self, message):
        pass

#start the bot
if __name__== "__main__":
    client = serverClient()
    client.run(client.getToken())