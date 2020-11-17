from pathlib import Path
from filehandling import FileHandler
from logger import Logger

class SettingsManager:
    def __init__(self):
        self.__settings = None
        self.__descriptions = None
        self.__helpMessages = None
        self.__onDefaultSettings = False
        logger: Logger = None

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
        self.__helpMesssages = fileHandler.loadJSON(helpMessagesPath)

    def saveSettings(self, fileHandler: FileHandler, logger: Logger):
        logger.writeToLog("Saving current settings to file!")
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
            
            if not self.checkForSetting(arg):
                print("Option '" + arg + "' does not exist!")
                return False
            
            optionType = self.checkForSettingType(arg)
            if isinstance(optionType,int):
                try:
                    value = int(value)
                except ValueError:
                    raise RuntimeError("Value for flag '{}' is of the wrong type!".format(arg))

            self.setOption(arg,value)
        return True

    #Gonna keep the compatibility for nested dicts in
    def __setOption(self,option,value,dictionairy: dict):
        for key,setting in dictionairy.items():
            if key == option:
                if type(setting) != type(value):
                    raise ValueError("Changing of setting type not permitted!")
                dictionairy[key] = value
                break
            if isinstance(setting,dict):
                self.__setOption(option,value,dictionairy[key])

    def setOption(self,option,value):
        return self.__setOption(option,value,self.getServerSettings())

    def __checkForSetting(self, settingName, dic) -> bool:
        exists = False
        
        for key,value in dic.items():
            if exists:
                break
            if key == settingName:
                exists = True
                break
            if isinstance(value,dic):
                exists = self.checkForSetting(settingName,dic[key])

        return exists

    def checkForSetting(self,settingName) -> bool:
        return self.__checkForSetting(settingName,self.getServerSettings())

    def __checkForSettingType(self, settingName, dic: dict) -> type:
        datatype = None

        for key,value in dic.items():
            if datatype != None:
                break
            if key == settingName:
                datatype = type(value)
                break
            if isinstance(value,dic):
                datatype = self.__checkForSettingType(settingName,dic[key])

        return datatype

    def checkForSettingType(self,settingName) -> type:
        return self.__checkForSettingType(settingName,self.__settings)

    def validateCriticalSettings(self) -> list:
        #Handle critical settings here to prevent crashes
        errorMessages: list = []
        if type(self.getServerSettings()["minRAM"]) != int:
            errorMessages.append("Argument minRAM has to be an integer!")
        if type(self.getServerSettings()["maxRAM"]) != int:
            errorMessages.append("Argument maxRAM has to be an integer!")
        return errorMessages

    def validateSettings(self) -> list:
        #Handle settings here
        errorMessages: list = []
        if self.getServerSettings()["maxRAM"] < self.getServerSettings()["minRAM"]:
            errorMessages.append("Argument minRAM is bigger than maxRAM!")
        if self.getServerSettings()["minRAM"] < 0:
            errorMessages.append("Argument minRAM cannot be smaller than or equal to zero!")
        if self.getServerSettings()["maxRAM"] == self.getServerSettings()["minRAM"]:
            errorMessages.append("Argument maxRAM has to be bigger than minRAM!")
        if self.getBotSettings()["standardChannel"] == "":
            errorMessages.append("No channel set for listening!")
        if self.getBotSettings()["checkRole"] == "":
            errorMessages.append("No role set for restricted access commands!")
        return errorMessages

    def __logSettings(self, settings, logger: Logger):
        for key, setting in settings.items():
            if isinstance(setting,dict):
                self.__logSettings(logger,setting)
            else:
                logger.writeToLog(self.__descriptions[key].format(setting))

    def logSettings(self, logger: Logger):
        if self.__onDefaultSettings:
            logger.writeToLog("No custom settings set! Running on default settings!")
        self.__logSettings(logger,self.__settings,self.__descriptions)

    #Check whether all implemented commands have a rank and helpMessage.
    #Only checking this way around not vice versa, 
    #since a helpMessage or ranking for a unimplemented command does not cause a crash.
    def checkCommandIntegrity(self, commandList) -> list:
        cmdRanks: dict = self.getCmdRanks()
        helpMessages: dict = self.getHelpMessages()
        errors = []

        helpMessagesCommandList = helpMessages.keys()
        commandList = commandList
        cmdRanksCommands = []
        for subdict in cmdRanks.values():
            cmdRanksCommands += subdict

        for command in commandList:
            if not command in helpMessagesCommandList:
                errors.append("Command {} does not have a helpMessage!".format(command))
            if not command in cmdRanksCommands:
                errors.append("Command {} does not have a ranking!".format(command))

        return errors


    def getDescriptions(self) -> dict:
        return self.__descriptions

    def getSettings(self) -> dict:
        return self.__settings

    def getCmdRanks(self) -> dict:
        return self.__settings["cmdRankSettings"]

    def getBotSettings(self) -> dict:
        return self.__settings["botSettings"]

    def getServerSettings(self) -> dict:
        return self.__settings["serverSettings"]

    def getHelpMessages(self) -> dict:
        return self.__helpMessages

    def onDefaultSettings(self) -> bool:
        return self.__onDefaultSettings