#!/usr/bin/python3
import discord
import asyncio
import os
import sys

from logger import Logger
from servermanager import ServerManager, ServerState
from filehandling import FileHandler
from settingsmanager import SettingsManager
from servermanager import ServerManager
from commands import MessageInterpreter

TOKENPATH = "../token.secret"

class ServerClient(discord.Client):
    def __init__(self,*,loop=None,**options):
        super().__init__()
        self.onReadyCallback: callable = None
        self.onMessageCallback: callable = self.__onMessage

    async def __onMessage(self,message: discord.Message):
        await message.channel.send("I am currently starting up. If this message concerns me please excuse me.")

    async def on_ready(self):
        await self.onReadyCallback()

    async def on_message(self, message: discord.Message):
        await self.onMessageCallback(message)

    def getToken(self):
        file = open(TOKENPATH)
        text = file.read()
        file.close()
        return text