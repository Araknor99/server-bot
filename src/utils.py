from filehandling import FileHandler
from servermanager import ServerManager
from settingsmanager import SettingsManager
from logger import Logger

class Utils:
    def __init__(self):
        self.fileHandler: FileHandler = FileHandler()
        self.sManager: SettingsManager = SettingsManager()
        self.server: ServerManager = ServerManager()
        self.logger: Logger = None

        self.deviceOpScheduled = False
        self.botClosing = False

    def initSettings(self,argv):
        self.sManager.loadSettings(self.fileHandler)

        if not self.sManager.interpretArgs(argv):
            return False

        if not self.sManager.validateSettings():
            return False

        if not self.sManager.checkCommandIntegrity():
            return False

        serverSettings = self.sManager.getServerSettings()
        settings = self.sManager.getBotSettings()

        self.logger = Logger(settings["logPath"],True)
        self.server.setArgs(serverSettings)

        self.sManager.logSettings(self.logger)
        self.logger.writeToLog("Ready!")
        return True

    def reloadSettings(self):
        self.logger.writeToLog("Loading new Settings...")
        self.sManager.loadSettings(self.fileHandler)
        self.logger.writeToLog("New settings loaded! Settings will take effect on server restart.")

    async def startServer(self):
        self.logger.writeToLog("Trying to start server...\nCurrent settings are:")
        self.sManager.logSettings(self.logger)

        serverSettings = self.sManager.getServerSettings()
        self.server.setArgs(serverSettings)
        if not self.server.openServer():
            self.logger.writeToLog("Unable to start server! Server is already running or processing operation!")
            return False

        self.logger.writeToLog("Server started!")
        return True

    async def closeServer(self):
        self.logger.writeToLog("Trying to close Server...")

        if not self.server.closeServer():
            self.logger.writeToLog("Unable to close Server! Server is already down or processing operation!")
            return False

        self.logger.writeToLog("Server closed!")
        self.logger.writeToLog("Dumping current settings to settings.json")
        return False

    #Close all utils and the server application
    async def closeBot(self):
        self.botClosing = True

        self.logger.writeToLog("Quitting bot!")
        if self.server.isRunning:
            self.closeServer()

        self.sManager.logSettings(self.logger)
        self.sManager.saveSettings()
        self.logger.endLog(self)
        
    #relay message to server
    async def relayMessage(self,message):
        self.logger.writeToLog("Relaying message to server! Content is:{}".format(message))
        self.server.printMessage(message)