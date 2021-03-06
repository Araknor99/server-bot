#!/usr/bin/python3
import discord
import sys

from bot import ServerClient
from utils import Utils
from commands import CommandsManager

class LifeCycle:
    def __init__(self):
        self.dClient: ServerClient = ServerClient()
        self.utils: Utils = Utils()
        self.interpreter: CommandsManager = None

    #Function to be called when a message arrives
    async def onMessageCallback(self,message):
        botSettings = self.utils.sManager.getBotSettings()

        channel = message.channel
        author: discord.Member = message.author
        authorName = author.name + "#" + author.discriminator

        if not self.interpreter.validContext(message):
            return

        if self.utils.botClosing:
            await channel.send("I am currently restarting or being shut down. Please wait a bit.")
            return

        self.utils.writeToLog("Recieved message from user '{}'!".format(authorName))
        self.utils.writeToLog("Message content:\n{}".format(message.content))

        if not self.interpreter.findCommand(message):
            self.utils.writeToLog("Given command is not valid!")
            await channel.send("That is not a valid command!\nUse {}help to get a list!".format(botSettings["checkSign"]))
            return

        if not self.interpreter.userHasPermission(message):
            self.utils.writeToLog("User is not permitted to request the given command!")
            await channel.send("You don't the permission to use that command!\nAsk a {}!".format(botSettings["checkRole"]))
            return
        
        await self.interpreter.executeCommand()

    async def initializeUtils(self):
        if not self.utils.initSettings(sys.argv):
            print("Something went wrong while initialising the utilities! Check your arguments and config files!\nExiting...\n")
            await self.dClient.close()
            sys.exit()
            
        self.interpreter = CommandsManager(self.utils,self.dClient)
        if not self.utils.checkCommandIntegrity(self.interpreter.commandList):
            print("Error in command integrity! Some commands are not fully implemented!\nExiting...\n")
            await self.dClient.close()
            sys.exit()

        self.dClient.onMessageCallback = self.onMessageCallback
        self.utils.writeToLog("Ready!")

    #initiliaze discord interface
    def initializeDiscord(self):
        self.dClient.onReadyCallback = self.initializeUtils
        self.dClient.run(self.dClient.getToken())

if __name__=="__main__":
    lifecycle = LifeCycle()
    lifecycle.initializeDiscord()