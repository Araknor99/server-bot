#!/usr/bin/python3
import discord

TOKENPATH = "../token.secret"

class ServerClient(discord.Client):
    def __init__(self,*,loop=None,**options):
        super().__init__()
        self.onReadyCallback: callable = None
        self.onMessageCallback: callable = self.__onMessage

    async def __onMessage(self,message: discord.Message):
        pass

    async def on_ready(self):
        await self.onReadyCallback()

    async def on_message(self, message: discord.Message):
        await self.onMessageCallback(message)

    def getToken(self):
        file = open(TOKENPATH)
        text = file.read()
        file.close()
        return text