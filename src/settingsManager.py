from pathlib import Path
from filehandling import FileHandler
from logger import Logger

class SettingsManager:
    def __init__(self):
        self.__settings = None
        self.__descriptions = None
        self.__helpMessages = None
        self.__onDefaultSettings = False

    def loadSettings(self,fileHandler: FileHandler):
        descriptionPath = "../settings/descriptions.json"
        helpMessagesPath = "../settings/helpMessages.json"
        path = "../settings/settings.json"

        self.__onDefaultSettings = False
        if not Path(path).is_file():
            path = "../settings/defaultSettings.json"
            self.__onDefaultSettings = True

        self.__settings = fileHandler.loadJSON(path)
        self.__descriptions = fileHandler.loadJSON(descriptionPath)
        self.__helpMesssages = fileHandler.loadJson(helpMessagesPath)

    def saveSettings(self,fileHandler: FileHandler):
        fileHandler.dumpJSON("../settings/settins.json",self.__settings)

    def interpretArgs(self,argv):
        #Check whether the flags have been set correctly
        #Might change functionality to support flags that need no value set
        #If the function cannot interpret the arguments then it returns False
        if len(argv) == 1:
            return True
            
        for i in range(1,len(argv),2):
            arg = argv[i]
            if arg[:2] == "--":
                try:
                    if i+1 > len(argv):
                        raise IndexError
                    value = argv[i+1]
                    if value[:2] == "--":
                        raise IndexError
                except IndexError:
                    print("No value for flag " + arg + ".\nExiting...")
                    return False
            else:
                print("No flag supplied for value: " + arg + ".\nExiting...")
                return False

        #Actually set the values
        for i in range(0,len(argv),2):
            arg = argv[i][2:]
            value = argv[i+1]
            
            #return False if the option does not exist so we can close the bot
            if not self.setOption(arg,value,self.__settings):
                print("Option '" + arg + "' does not exist!")
                return False
        return True

    #Gonna keep the compatibility for nested dicts in
    def __setOption(self,option,value,dictionairy):
        for key,setting in dictionairy.items():
            if isinstance(setting,dict):
                return self.__setOption(option,value,dictionairy[key])
            if key == option:
                if isinstance(setting,int):
                    value = int(value)
                dictionairy[key] = value
                return True
        return False

    def setOption(self,option,value):
        return self.__setOption(option,value,self.__settings)

    def validateSettings(self):
        if self.getServerSettings()["maxRAM"] < self.getServerSettings()["minRAM"]:
            print("Argument minRAM is bigger than maxRAM! Exiting...")
            return False
        if self.getBotSettings()["standardChannel"] == "":
            print("No channel for listening has been set! Exiting...")
            return False
        if self.getBotSettings()["checkRole"] == "":
            print("No role set for restricted access commands! Exiting...")
        return True

    def __logSettings(self,logger: Logger,settings):
        for key, setting in settings.items():
            if isinstance(setting,dict):
                self.__logSettings(logger,setting)
            else:
                logger.writeToLog(self.__descriptions[key].format(setting))

    def logSettings(self,logger: Logger):
        if self.__onDefaultSettings:
            logger.writeToLog("No custom settings set! Running on default settings!")
        self.__logSettings(logger,self.__settings,self.__descriptions)

    #Check whether all the commands in the cmdRanks are in the helpMessages.json
    #Will have to find a way to check whether all commands in commands.py are implemented in these files
    def checkCommandIntegrity(self):
        cmdRanks: dict = self.getCmdRanks()
        helpMessages: dict = self.getHelpMessages()
        integrity = True

        for subdict in cmdRanks.values():
            for command in subdict:
                if command not in helpMessages.keys():
                    print("Command {} from cmdRanks not present in helpMessages.json!".format(command))
                    integrity = False

        for command in helpMessages.keys():
            for subdict in cmdRanks.values():
                if command not in subdict:
                    print("Command {} from helpMessages.json not present in cmdRanks!".format(command))
                    integrity = False

        return integrity

    def getDescriptions(self):
        return self.__descriptions

    def getSettings(self):
        return self.__settings

    def getCmdRanks(self):
        return self.__settings["cmdRankSettings"]

    def getBotSettings(self):
        return self.__settings["botSettings"]

    def getServerSettings(self):
        return self.__settings["serverSettings"]

    def getHelpMessages(self):
        return self.__helpMessages

    def onDefaultSettings(self):
        return self.__onDefaultSettings