from abc import ABC,abstractmethod
from utils import Utils
from servermanager import ServerManager,ServerState
from filehandling import FileHandler

import os
import discord
import urllib.request
import asyncio

class MessageInterpreter():
    def __init__(self,utils: Utils):
        self.commands = [State,Ip,Help,StartServer,CloseServer,RestartDevice,ShutdownDevice,ListArgs,SetArg,QuitBot]
        self.cCommand: Command = None
        self.utils = utils

    def validContext(self,message: discord.Message):
        botSettings = self.utils.sManager.getBotSettings()
        if message.channel.name != botSettings["standardChannel"]:
            return False

        if message.content.find(botSettings["checkSign"] != 0):
            return False

        return True

    def asParts(self,message: str):
        botSettings = self.utils.sManager.getBotSettings()
        checkSign = botSettings["checkSign"]

        parts = message.split(checkSign)
        parts[0].replace(checkSign,"",1)

        return parts

    def findCommand(self,message: discord.Message):
        name = self.asParts(message.content)[0]

        #ref as short for reference
        for ref in commands:
            command = ref(self.asParts(message))
            if command.name == name:
                self.cCommand = command
                return True
        return False

    def userHasPermission(self,message: discord.Message):
        botSettings = self.utils.sManager.getBotSettings()
        cmdSettings = self.utils.sManager.getCmdRanks()

        author: discord.Member = message.author
        roles = author.roles
        command = self.asParts(message.content)[0]

        if command in cmdSettings["lowerRank"]:
            return True

        for role in roles:
            if role.name == botSettings["checkRole"]:
                return True
        return False

    async def executeCommand(self):
        if self.cCommand == None:
            raise RuntimeError("No command set but trying to execute!\nRaising error!")

        if not self.cCommand.checkArgs():
            return

        await self.cCommand.execute()




#############################################
# The actual implementation of the commands #
#############################################
class Command(ABC):
    def __init__(self,messageParts, channel, utils):
        self.name = ""
        self.messageParts: dict = messageParts
        self.channel: discord.TextChannel = channel
        self.utils: Utils = utils
        super().__init__()

    @abstractmethod
    def checkArgs(self):
        pass

    @abstractmethod
    def execute(self):
        pass

class State(Command):
    def __init__(self, messageParts, channel, utils):
        super().__init__(messageParts, channel, utils)
        self.name = "state"

    def checkArgs(self):
        return True

    async def execute(self):
        state = self.utils.server.getState()

        if state == ServerState.KILLED:
            await self.channel.send("Server process has been killed! Did something happen?")
        elif state == ServerState.DOWN:
            await self.channel.send("The server is currently offline.")
        elif state == ServerState.PROCESSING:
            await self.channel.send("The server is currently processing an operation.")
        elif state == ServerState.RUNNING:
            playerCount = self.utils.server.getPlayerCount()
            await self.channel.send("The server is online!\nThere are currently {} players on it!".format(playerCount))
    

class Ping(Command):
    def __init__(self, messageParts, channel, utils):
        super().__init__(messageParts, channel, utils)
        self.name = "ping"

    def checkArgs(self):
        return True

    async def execute(self):
        await self.channel.send("The current latency is {}ms!".format(int(self.utils.latency * 1000)))

class Ip(Command):
    def __init__(self, messageParts, channel, utils):
        super().init(messageParts, channel, utils)
        self.name = "ip"

    def checkArgs(self):
        return True

    async def execute(self):
        externalIP = urllib.request.urlopen("https://api.ipify.org").read().decode("utf-8")
        await self.channel.send("The current IP of the server is: " + externalIP)

class Help(Command):
    def __init__(self, messageParts, channel, utils):
        super().__init__(messageParts, channel, utils)
        self.name = "help"
        self.message = "Commands:\n\n"

    def checkArgs(self):
        return True

    def addCmdsToMessage(self,messages,cmdRanks,checkSign):
        longest = len(max(messages.keys,key=len))
        for cmd in cmdRanks:
            msg = messages[cmd]
            spaces = longest - len(cmd)
            part = "{}{}{}{} - {}\n".format(checkSign,cmd,spaces * " ",msg)
            self.message += part

    async def execute(self):
        checkSign = self.utils.sManager.getBotSettings()["checkSign"]
        cmdRanks = self.utils.sManager.getCmdRanks()
        fHandler: FileHandler = self.utils.fileHandler
        
        messages: dict = fHandler.loadJSON("../settings/helpMessages.json")
        
        self.message += "Unrestricted commands:\n"
        self.addCmdsToMessage(messages,cmdRanks["lowerRank"])

        self.message += "\nCommands with restricted access:\n"
        self.addCmdsToMessage(messages,cmdRanks["higherRank"])

        result = "```" + self.message + "```"
        await self.channel.send(result)


class StartServer(Command):
    def __init__(self, messageParts, channel, utils):
        super().__init__(messageParts, channel, utils)
        self.name = "startserver"

    def checkArgs(self):
        return True

    async def execute(self):
        await self.channel.send("Dumping current settings into savefile...")
        self.utils.sManager.saveSettings()
        await self.channel.send("Trying to start server...")

        if not await self.utils.startServer():
            await self.channel.send("Cannot start server! Is it already running?")
        await self.channel.send("Server started! Have fun")

class CloseServer(Command):
    def __init__(self, messageParts, channel, utils):
        super().__init__(messageParts, channel, utils)
        self.name = "closeserver"

    def checkArgs(self):
        return True

    async def execute(self):
        await self.channel.send("Trying to close server...")
        if not await self.utils.closeServer():
            await self.channel.send("Unable to close server! Is it already down?")
        await self.channel.send("Server Closed!")

class RestartDevice(Command):
    pass

class ShutdownDevice(Command):
    pass

class ListArgs(Command):
    pass

class SetArg(Command):
    pass

class QuitBot(Command):
    pass