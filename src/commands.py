from abc import ABC,abstractmethod
from bot import ServerClient
from utils import Utils
from servermanager import ServerManager,ServerState
from filehandling import FileHandler

import os
import discord
import urllib.request
import asyncio
import time

class CommandsManager():
    def __init__(self,utils: Utils):
        self.commands = [State,Ip,Help,StartServer,CloseServer,RestartDevice,ShutdownDevice,ListArgs,CancelOperation,SetArg,ListDeviceOp]
        self.cCommand: Command = None
        self.cDeviceOp: Command = None
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
        for ref in self.commands:
            command = ref(self.asParts(message), message.channel, self.utils, self.cDeviceOp)
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

        if not await self.cCommand.checkArgs():
            return

        await self.cCommand.execute()




#############################################
# The actual implementation of the commands #
#############################################
class Command(ABC):
    def __init__(self,messageParts, channel, utils, cDeviceOp):
        self.name = ""
        self.messageParts: dict = messageParts
        self.channel: discord.TextChannel = channel
        self.utils: Utils = utils
        self.cDeviceOp: Command = cDeviceOp
        self.cancelRequested = False
        super().__init__()

    async def checkArgs(self) -> bool:
        return True

    @abstractmethod
    async def execute(self):
        pass

class State(Command):
    def __init__(self, messageParts, channel, utils, cDeviceOp):
        super().__init__(messageParts, channel, utils, cDeviceOp)
        self.name = "state"

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
    def __init__(self, messageParts, channel, utils, cDeviceOp):
        super().__init__(messageParts, channel, utils, cDeviceOp)
        self.name = "ping"

    async def execute(self):
        await self.channel.send("The current latency is {}ms!".format(int(self.utils.latency * 1000)))

class Ip(Command):
    def __init__(self, messageParts, channel, utils, cDeviceOp):
        super().init(messageParts, channel, utils, cDeviceOp)
        self.name = "ip"

    async def execute(self):
        externalIP = urllib.request.urlopen("https://api.ipify.org").read().decode("utf-8")
        await self.channel.send("The current IP of the server is: " + externalIP)

class Help(Command):
    def __init__(self, messageParts, channel, utils, cDeviceOp):
        super().__init__(messageParts, channel, utils, cDeviceOp)
        self.name = "help"
        self.message = "Commands:\n\n"

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
        messages = self.utils.sManager.getHelpMessages()
        
        self.message += "Unrestricted commands:\n"
        self.addCmdsToMessage(messages, cmdRanks["lowerRank"], checkSign)

        self.message += "\nCommands with restricted access:\n"
        self.addCmdsToMessage(messages, cmdRanks["higherRank"], checkSign)

        result = "```" + self.message + "```"
        await self.channel.send(result)


class StartServer(Command):
    def __init__(self, messageParts, channel, utils, cDeviceOp):
        super().__init__(messageParts, channel, utils, cDeviceOp)
        self.name = "startserver"

    async def execute(self):
        checkRole = self.utils.sManager.getBotSettings()["checkRole"]
        await self.channel.send("Trying to start server...")

        if not self.utils.sManager.validateSettings():
            await self.channel.send("Cannot start server! Settings are invalid!\n Please contact someone with the role '{}'!".format(checkRole))
            return

        self.utils.sManager.saveSettings()

        if not await self.utils.startServer():
            await self.channel.send("Cannot start server! Is it already running or starting upo?")
        await self.channel.send("Server started! Have fun")

class CloseServer(Command):
    def __init__(self, messageParts, channel, utils, cDeviceOp):
        super().__init__(messageParts, channel, utils, cDeviceOp)
        self.name = "closeserver"

    async def execute(self):
        await self.channel.send("Trying to close server...")
        if not await self.utils.closeServer():
            await self.channel.send("Unable to close server! Is it already offline or shutting down?")
        await self.channel.send("Server Closed!")

#TODO: implement timeOfStart
class RestartDevice(Command):
    def __init__(self, messageParts, channel, utils, cDeviceOp):
        super().__init__(messageParts, channel, utils, cDeviceOp)
        self.name = "restartdevice"
        self.time = 0
        self.timeOfStart = None

    async def checkArgs(self) -> bool:
        if len(self.messageParts) == 1:
            await self.channel.send("Please specify a time interval in minutes.")
            return False
        
        self.time = int(self.messageParts[1])
        return True

    async def execute(self):
        if self.utils.deviceOpScheduled:
            await self.channel.send("Device Operation already scheduled! Cancel it to set another!")
            return

        if self.utils.server.isRunning():
            self.utils.relayMessage("Restarting in {} minutes!".format(self.time))
        
        self.cDeviceOp = self

        time.sleep(self.time * 60);
        if not self.cancelRequested:
            self.utils.closeBot()
            os.system("shutdown 0")

#TODO: implement timeOfStart
class ShutdownDevice(Command):
    def __init__(self, messageParts, channel, utils, cDeviceOp):
        super().__init__(messageParts, channel, utils, cDeviceOp)
        self.name = "shutdowndevice"
        self.time = 0
        self.timeOfStart = None

    async def checkArgs(self) -> bool:
        if len(self.messageParts) == 1:
            await self.channel.send("Please specify a time interval in minutes.")
            return False

        self.time = int(self.messageParts[1])
        return True
    
    async def execute(self):
        if self.utils.deviceOpScheduled:
            await self.channel.send("Device Operation already scheduled! Cancel it to set another!")
            return
        
        if self.utils.server.isRunning():
            self.utils.relayMessage("Shutting down in {} minutes!".format(self.time))

        self.cDeviceOp = self

        time.sleep(self.time * 60);
        if not self.cancelRequested:
            self.utils.closeBot()
            os.system("reboot")

class ListArgs(Command):
    def __init__(self, messageParts, channel, utils, cDeviceOp):
        super().__init__(messageParts, channel, utils, cDeviceOp)
        self.name = "listargs"
        self.message = "The settings are the following:\n"

    def __expandMessage(self, options: dict, desc: dict):
        for key,value in options.items():
            if isinstance(value,dict):
                self.__expandMessage(options[key],desc)
            else:
                self.message += "    " + desc[key].format(value) + "\n"

    async def execute(self):
        desc = self.utils.sManager.getDescriptions()
        options = self.utils.sManager.getSettings()
        self.__expandMessage(options, desc)

        await self.channel.send(self.message)

class SetArg(Command):
    def __init__(self, messageParts, channel, utils, cDeviceOp):
        super().__init__(messageParts, channel, utils, cDeviceOp)
        self.name = "setarg"

    async def checkArgs(self) -> bool:
        checkSign = self.utils.sManager.getBotSettings["checkSign"]

        if len(self.messageParts) < 3:
            await self.channel.send("Not enough arguments specified!\n Use {}help to get info on usage.".format(checkSign))
            return False

        return True

    #TODO: finish this function 
    async def execute(self):
        setting = self.messageParts[1]
        value = self.messageParts[2]
        checkSign = self.utils.sManager.getBotSettings["checkSign"]

        if not self.utils.sManager.checkForSetting(setting):
            await self.channel.send("The setting '{}{}' does not exist!\nUse {}listargs for a list of commands!".format(checkSign,setting,checkSign))
            return
        
        dataype = self.utils.sManager.checkForSettingType(setting)
        if isinstance(dataype,int):
            try:
                value = int(value)
            except ValueError:
                await self.channel.send("Your value for the given setting has to be a number!")
                return
            
        self.utils.sManager.setOption(setting,value)

class CancelOperation(Command):
    def __init__(self, messageParts, channel, utils, cDeviceOp):
        super().__init__(messageParts, channel, utils, cDeviceOp)
        self.name = "listargs"

    async def execute(self):
        checkSign = self.utils.sManager.getBotSettings["checkSign"]

        if(self.cDeviceOp == None):
            await self.channel.send("Currently no device operation planned!\n Use '{}listop'".format(checkSign))
            return
        
        self.cDeviceOp.cancelRequested = True

#TODO: finish this function!
class ListDeviceOp(Command):
    def __init__(self, messageParts, channel, utils, cDeviceOp):
        super().__init__(messageParts, channel, utils, cDeviceOp)
        self.name = "listdeviceop"

    async def execute(self):
        if self.cDeviceOp == None:
            await self.channel.send("No device operation planned!")
        elif self.cDeviceOp.name == "restartdevice":
            time = self.cDeviceOp.time
            await self.channel.send("Planning a restart of the device in {minutes} ")