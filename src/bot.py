import discord
import sys

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
        try:
            file = open(TOKENPATH)
            text = file.read()
            file.close()
            return text
        except:
            print("Unable to read the Token! Did you put it in the proper place?")
            sys.exit()