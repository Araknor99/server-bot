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

        self.logSettings()
        return True

    def reloadSettings(self):
        self.writeToLog("Loading new Settings...")
        self.sManager.loadSettings(self.fileHandler)
        self.rwriteToLog("New settings loaded! Settings will take effect on server restart.")

    def setOption(self,option,value):
        self.writeToLog("Setting option {} to {}".format(option,value))
        self.sManager.setOption(option,value)

    def interpretArgs(self, argv):
        self.writeToLog("Interpreting console arguments...")
        return self.sManager.interpretArgs(argv)

    def checkCommandIntegrity(self, commandList):
        self.writeToLog("Checking integrity of implemented commands...")
        errors = self.sManager.checkCommandIntegrity(commandList)

        if errors != []:
            for error in errors:
                self.writeToLog("ERR: {}".format(error))
            return False
        return True

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

    def saveSettings(self):
        self.writeToLog("Saving settings to file!")
        self.logSettings()
        self.sManager.saveSettings(self.fileHandler)

    def logSettings(self):
        if self.sManager.onDefaultSettings():
            self.writeToLog("Currently working on default settings!")
        msg = "Current settings: \n" + self.sManager.logSettings()
        self.writeToLog(msg)
        
    async def startServer(self):
        self.writeToLog("Trying to start server...")

        self.validateSettings()
        self.saveSettings()

        serverSettings = self.sManager.getServerSettings()
        self.server.setArgs(serverSettings)
        if not self.server.openServer():
            self.writeToLog("Unable to start server! Server is already running!")
            return False

        self.writeToLog("Server started!")
        return True

    def closeServer(self):
        self.writeToLog("Trying to close Server...")

        if not self.server.closeServer():
            self.writeToLog("Unable to close Server! Server is already down!")
            return False

        self.writeToLog("Server closed!")
        self.writeToLog("Dumping current settings to settings.json")
        return True

    #Close all utils and the server application
    def closeBot(self):
        self.botClosing = True

        self.writeToLog("Quitting bot!")
        if self.server.isRunning:
            self.relayMessage("Server is shutting down!")
            self.closeServer()

        self.logSettings()
        self.saveSettings()
        self.logger.endLog()

    def shutdown(self):
        self.writeToLog("Shutting down!")
        self.closeBot()
        os.system("shutdown 0")

    def restart(self):
        self.writeToLog("Restarting!")
        self.closeBot()
        os.system("shutdown -r 0")
        
    #relay message to server
    async def relayMessage(self, message):
        self.writeToLog("Relaying message to server! Content is:{}".format(message))
        self.server.printMessage(message)