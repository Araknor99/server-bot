from filehandling import FileHandler
from servermanager import ServerManager
from settingsmanager import SettingsManager
from deviceopscheduler import DeviceOpScheduler
from logger import Logger

import os

class Utils:
    def __init__(self):
        self.fileHandler: FileHandler = FileHandler()
        self.sManager: SettingsManager = SettingsManager()
        self.server: ServerManager = ServerManager()
        self.scheduler: DeviceOpScheduler = DeviceOpScheduler()
        self.logger: Logger = None

        self.botClosing = False

    def writeToLog(self, msg: str):
        if self.logger == None:
            print(msg)
        else:
            self.logger.writeToLog(msg)

    def initSettings(self, argv):
        self.writeToLog("Initializing settings...")
        self.sManager.loadSettings(self.fileHandler)

        if not self.interpretArgs(argv):
            return False

        if not self.validateSettings():
            return False

        serverSettings = self.sManager.getServerSettings()
        settings = self.sManager.getBotSettings()

        self.logger = Logger(settings["logPath"],True)
        self.server.setArgs(serverSettings)

        self.sManager.logSettings(self.logger)
        self.writeToLog("Ready!")
        return True

    def reloadSettings(self):
        self.writeToLog("Loading new Settings...")
        self.sManager.loadSettings(self.fileHandler)
        self.rwriteToLog("New settings loaded! Settings will take effect on server restart.")

    def interpretArgs(self, argv):
        self.writeToLog("Interpreting console arguments...")
        return self.sManager.interpretArgs(argv)

    def checkCommandIntegrity(self, commandList):
        self.writeToLog("Checking integrity of implemented commands...")
        return self.sManager.checkCommandIntegrity(commandList)

    def validateSettings(self):
        self.writeToLog("Validating settings...")
        
        errors: list = self.sManager.validateCriticalSettings()
        if errors != []:
            for error in errors:
                self.writeToLog("ERR: " + error)
            return False

        errors = self.sManager.validateSettings()
        if errors != []:
            for error in errors:
                self.writeToLog("ERR: " + error)
            return False
        return True
        

    async def startServer(self):
        self.writeToLog("Trying to start server...\nCurrent settings are:")
        self.sManager.logSettings(self.logger)

        serverSettings = self.sManager.getServerSettings()
        self.server.setArgs(serverSettings)
        if not self.server.openServer():
            self.writeToLog("Unable to start server! Server is already running or processing operation!")
            return False

        self.writeToLog("Server started!")
        return True

    async def closeServer(self):
        self.writeToLog("Trying to close Server...")

        if not self.server.closeServer():
            self.writeToLog("Unable to close Server! Server is already down or processing operation!")
            return False

        self.writeToLog("Server closed!")
        self.writeToLog("Dumping current settings to settings.json")
        return False

    #Close all utils and the server application
    async def closeBot(self):
        self.botClosing = True

        self.writeToLog("Quitting bot!")
        if self.server.isRunning:
            self.closeServer()

        self.sManager.logSettings(self.logger)
        self.sManager.saveSettings(self.logger)
        self.logger.endLog(self)

    async def shutdown(self):
        self.writeToLog("Shutting down!")
        await self.closeBot()
        os.system("shutdown now")

    async def restart(self):
        self.writeToLog("Restarting!")
        await self.closeBot()
        os.system("shutdown -r 0")
        
    #relay message to server
    async def relayMessage(self, message):
        self.writeToLog("Relaying message to server! Content is:{}".format(message))
        self.server.printMessage(message)