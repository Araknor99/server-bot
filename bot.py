import discord
from logger import Logger
from servermanager import ServerManager, ServerState

LOGPATH = "log.txt"

class serverClient(discord.Client):
    def __init__(self):
        super.__init__()
        self.__logger = Logger(LOGPATH)
        self.__servermanager = ServerManager("./server/paper.jar")

    async def on_ready(self):
        pass
