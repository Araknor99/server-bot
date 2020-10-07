#!/usr/bin/python3
import discord
import asyncio
from logger import Logger
from servermanager import ServerManager, ServerState
from filehandling import FileHandler
from settingsmanager import SettingsManager
from servermanager import ServerManager
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
        self.__server = ServerManager()

        if not self.__sManager.interpretArgs(argv):
            await self.close()
            return

        if not self.__sManager.validateSettings():
            await self.close()
            return

        serverSettings = self.__sManager.getServerSettings()
        settings = self.__sManager.getSettings()

        self.__logger = Logger(settings["logPath"],True)
        
        self.__server.setArgs(serverSettings)
        self.__sManager.logSettings(self.__logger)
        
        self.__ready = True
        self.__logger.writeToLog("Ready!")

    def getToken(self):
        file = open(TOKENPATH)
        text = file.read()
        file.close()
        return text

    def reloadSettings(self):
        self.__logger.writeToLog("Loading new Settings...")
        self.__sManager.loadSettings(self.__fileHandler)
        self.__logger.wirteToLog("New settings loaded! Settings will take effect on server restart.")

    #TODO: finish the function.
    #      Needs to be able to start the server and log the settings
    async def startServer(self):
        self.__logger.writeToLog("Trying to start server...\nCurrent settings are:")
        self.__sManager.logSettings(self.__logger)

        serverSettings = self.__sManager.getServerSettings()
        self.__server.setArgs(serverSettings)
        if not self.__server.openServer():
            self.__logger.writeToLog("Unable to start server! Server is already running or processing operation!")
            return False

        self.__logger.writeToLog("Server started!")
        return True

    async def closeServer(self):
        self.__logger.writeToLog("Trying to close Server...")

        if not self.__server.closeServer():
            self.__logger.writeToLog("Unable to close Server! Server is already down or processing operation!")
            return False

        self.__logger.writeToLog("Server closed!")
        return False


    #-------------------------------------------------------------
    #| These functions do all the user interaction and bot stuff |
    #-------------------------------------------------------------
    #TODO finish this function
    def checkMessage(self, message: discord.Message):
        pass

    async def on_ready(self):
        print("Warming up the utilities...")
        self.__ready = False
        await self.onReadyInit(sys.argv[1:])

    #TODO finish this function
    async def on_message(self, message):
        pass

#start the bot
if __name__== "__main__":
    print("Starting the client...")
    client = serverClient()
    client.run(client.getToken())