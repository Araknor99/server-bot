from abc import ABC,abstractmethod
from inspect import indentsize
from bot import ServerClient
from utils import Utils
from servermanager import ServerManager,ServerState
from filehandling import FileHandler

import os
import discord
import urllib.request
import asyncio
import time
import datetime
import sys

class CommandsManager():
    def __init__(self, utils: Utils, disClient: ServerClient):
        self.commands = [State,Ping,Ip,Help,StartServer,CloseServer,RestartDevice,ShutdownDevice,ListArgs,CancelOperation,SetArg,ListDeviceOp,QuitBot]
        self.cCommand: Command = None
        self.utils = utils
        self.disClient = disClient
        self.commandList = self.__createCommandsList()

    def __createCommandsList(self):
        commandList = []
        for whatCommand in self.commands:
            command: Command = whatCommand(None,None,None,None)
            commandList.append(command.name)
        return commandList

    def validContext(self, message: discord.Message):
        botSettings = self.utils.sManager.getBotSettings()
        if message.channel.name != botSettings["standardChannel"]:
            return False

        if message.content.find(botSettings["checkSign"]) != 0:
            return False

        return True

    def asParts(self, message: str):
        botSettings = self.utils.sManager.getBotSettings()
        checkSign = botSettings["checkSign"]

        parts = message.split(" ")
        parts[0] = parts[0].replace(checkSign,"",1)

        return parts

    def findCommand(self, message: discord.Message):
        name = self.asParts(message.content)[0]

        #ref as short for reference
        for ref in self.commands:
            command = ref(self.asParts(message.content), message.channel, self.utils, self.disClient)
            if command.name == name:
                self.cCommand = command
                return True
        return False

    def userHasPermission(self, message: discord.Message):
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

        if not await self.cCommand.checkArgs():
            return

        loop = asyncio.get_event_loop()
        loop.create_task(self.cCommand.execute())




#############################################
# The actual implementation of the commands #
#############################################
class Command(ABC):
    def __init__(self, messageParts, channel, utils, bot):
        self.name = ""
        self.messageParts: dict = messageParts
        self.channel: discord.TextChannel = channel
        self.utils: Utils = utils
        self.bot: ServerClient = bot
        super().__init__()

    async def checkArgs(self) -> bool:
        return True

    @abstractmethod
    async def execute(self):
        pass

class State(Command):
    def __init__(self, messageParts, channel, utils, bot):
        super().__init__(messageParts, channel, utils, bot)
        self.name = "state"

    async def execute(self):
        state = self.utils.server.getState()

        if state == ServerState.KILLED:
            await self.channel.send("Server process has been killed! Did something happen?")
        elif state == ServerState.DOWN:
            await self.channel.send("The server is currently offline.")
        elif state == ServerState.RUNNING:
            playerCount = self.utils.server.getPlayerCount()
            await self.channel.send("The server is online!\nThere are currently {} players on it!".format(playerCount))
    

class Ping(Command):
    def __init__(self, messageParts, channel, utils, bot):
        super().__init__(messageParts, channel, utils, bot)
        self.name = "ping"

    async def execute(self):
        await self.channel.send("The current latency is {}ms!".format(int(self.bot.latency * 1000)))

class Ip(Command):
    def __init__(self, messageParts, channel, utils, bot):
        super().__init__(messageParts, channel, utils, bot)
        self.name = "ip"

    async def execute(self):
        externalIP = urllib.request.urlopen("https://api.ipify.org").read().decode("utf-8")
        await self.channel.send("The current IP of the server is: " + externalIP)

class Help(Command):
    def __init__(self, messageParts, channel, utils, bot):
        super().__init__(messageParts, channel, utils, bot)
        self.name = "help"
        self.message = "Commands:\n\n"

    def addCmdsToMessage(self,messages,cmdRanks,checkSign):
        longest = len(max(messages.keys(),key=len))
        for cmd in cmdRanks:
            msg = messages[cmd]
            if "{}" in msg:
                msg = msg.format(checkSign)

            spaces = longest - len(cmd)
            part = "{}{}{} - {}\n".format(checkSign,cmd,spaces * " ",msg)
            self.message += part

    async def execute(self):
        checkSign = self.utils.sManager.getBotSettings()["checkSign"]
        cmdRanks = self.utils.sManager.getCmdRanks()
        messages = self.utils.sManager.getHelpMessages()
        
        self.message += "Unrestricted commands:\n"
        self.addCmdsToMessage(messages, cmdRanks["lowerRank"], checkSign)

        self.message += "\nCommands with restricted access:\n"
        self.addCmdsToMessage(messages, cmdRanks["higherRank"], checkSign)

        result = "```" + self.message + "```"
        await self.channel.send(result)


class StartServer(Command):
    def __init__(self, messageParts, channel, utils, bot):
        super().__init__(messageParts, channel, utils, bot)
        self.name = "startserver"

    async def execute(self):
        await self.channel.send("Trying to start server. This might take a while...")

        if not self.utils.startServer():
            await self.channel.send("Cannot start server! Please check state and settings!")
            return
        await self.channel.send("Server started! Have fun!")

class CloseServer(Command):
    def __init__(self, messageParts, channel, utils, bot):
        super().__init__(messageParts, channel, utils, bot)
        self.name = "closeserver"

    async def execute(self):
        await self.channel.send("Trying to close server. This might take a while...")
        if not self.utils.closeServer():
            await self.channel.send("Unable to close server! Is it already offline or shutting down?")
            return
        await self.channel.send("Server Closed!")

class ListArgs(Command):
    def __init__(self, messageParts, channel, utils, bot):
        super().__init__(messageParts, channel, utils, bot)
        self.name = "listargs"
        self.message = "The settings are the following:\n```"
        self.volume = 0

    def __expandMessage(self, options: dict, desc: dict):
        for key,value in options.items():
            if isinstance(value,dict):
                self.__expandMessage(options[key],desc)
            else:
                description = desc[key].format(value)
                argLength = len(key)

                self.message += "    > {}{} - {}\n".format(key, (self.volume-argLength) * " ", description)

    async def execute(self):
        desc = self.utils.sManager.getDescriptions()
        options = self.utils.sManager.getServerSettings()

        self.volume = len(max(options.keys(),key=len)) + 1

        self.__expandMessage(options, desc)
        self.message += "```"

        await self.channel.send(self.message)

class SetArg(Command):
    def __init__(self, messageParts, channel, utils, bot):
        super().__init__(messageParts, channel, utils, bot)
        self.name = "setarg"

    async def checkArgs(self) -> bool:
        checkSign = self.utils.sManager.getBotSettings()["checkSign"]

        if len(self.messageParts) < 3:
            await self.channel.send("Not enough arguments specified!\n Use {}help to get info on usage.".format(checkSign))
            return False

        return True

    async def execute(self):
        setting = self.messageParts[1]
        value = self.messageParts[2]
        checkSign = self.utils.sManager.getBotSettings()["checkSign"]

        if not self.utils.sManager.checkForSetting(setting):
            await self.channel.send("The setting '{}{}' does not exist!\nUse {}listargs for a list of commands!".format(checkSign,setting,checkSign))
            return
        
        datatype = self.utils.sManager.checkForSettingType(setting)
        if datatype == int:
            try:
                value = int(value)
            except ValueError:
                await self.channel.send("Your value for the given setting has to be a number!")
                return
            
        self.utils.sManager.setOption(setting,value)
        await self.channel.send("Parameter has been set!")

class RestartDevice(Command):
    def __init__(self, messageParts, channel, utils, bot):
        super().__init__(messageParts, channel, utils, bot)
        self.name = "restartdevice"

    async def checkArgs(self) -> bool:
        if len(self.messageParts) == 1:
            await self.channel.send("Please specify a time interval in minutes.")
            return False
        
        self.time = int(self.messageParts[1])
        return True

    async def execute(self):
        if self.utils.scheduler.eventScheduled():
            await self.channel.send("Device Operation already scheduled! Cancel it to set another!")
            return

        if self.utils.server.isRunning():
            self.utils.relayMessage("Restarting in {} minutes!".format(self.time))
        
        timepoint = datetime.datetime.now() + datetime.timedelta(minutes=self.time)
        self.utils.scheduler.setEvent(timepoint,self.utils.restart)
        

class ShutdownDevice(Command):
    def __init__(self, messageParts, channel, utils, bot):
        super().__init__(messageParts, channel, utils, bot)
        self.name = "shutdowndevice"

    async def checkArgs(self) -> bool:
        if len(self.messageParts) == 1:
            await self.channel.send("Please specify a time interval in minutes.")
            return False

        self.time = int(self.messageParts[1])
        return True
    
    async def execute(self):
        if self.utils.scheduler.eventScheduled():
            await self.channel.send("Device Operation already scheduled! Cancel it to set another!")
            return
        
        if self.utils.server.isRunning():
            self.utils.relayMessage("Shutting down in {} minutes!".format(self.time))

        timepoint = datetime.datetime.now() + datetime.timedelta(minutes = self.time)
        self.utils.scheduler.setEvent(timepoint,self.utils.restart)

class CancelOperation(Command):
    def __init__(self, messageParts, channel, utils, bot):
        super().__init__(messageParts, channel, utils, bot)
        self.name = "canceloperation"

    async def execute(self):
        checkSign = self.utils.sManager.getBotSettings()["checkSign"]

        if(not self.utils.scheduler.eventScheduled()):
            await self.channel.send("Currently no device operation planned!\n Use '{}listdeviceop'".format(checkSign))
            return

        self.utils.scheduler.stopScheduledOp()
        await self.channel.send("Scheduled event has been canceled!")
        

#TODO: finish this function!
class ListDeviceOp(Command):
    def __init__(self, messageParts, channel, utils, bot):
        super().__init__(messageParts, channel, utils, bot)
        self.name = "listdeviceop"
        self.timeDiff: datetime.timedelta = None

    async def execute(self):
        if self.utils.scheduler.eventScheduled():
            self.timeDiff = self.utils.scheduler.howLongTill()
        else:
            await self.channel.send("There is currently no operation scheduled!")
            return

        s = self.timeDiff.seconds
        m = int(s/60)

        if self.utils.scheduler.getEventType() == "restartdevice":
            await self.channel.send("Planning a restart of the device in {} minutes and {} seconds!".format(m,s))
        elif self.utils.scheduler.getEventType() == "shutdowndevice":
            await self.channel.send("Planning a restart of the device in {} minutes and {} seconds!".format(m,s))

class QuitBot(Command):
    def __init__(self, messageParts, channel, utils, bot):
        super().__init__(messageParts, channel, utils, bot)
        self.name = "quitbot"

    async def execute(self):
        await self.channel.send("Closing bot...")

        if self.utils.server.isRunning():
            await self.channel.send("Please close the server before closing the bot!")
            return
        
        self.utils.closeBot()
        await self.channel.send("Bot will now go offline!")
        await self.bot.close()
        sys.exit()