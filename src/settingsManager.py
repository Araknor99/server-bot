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
    def __setOption(self,option,value,dictionairy):
        for key,setting in dictionairy.items():
            if key == option:
                if type(setting) != type(value):
                    raise ValueError("Changing of setting type not permitted!")
                dictionairy[key] = value
                break
            if isinstance(setting,dict):
                self.__setOption(option,value,dictionairy[key])

    def setOption(self,option,value):
        return self.__setOption(option,value,self.__settings)

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
        return self.__checkForSetting(settingName,self.__settings)

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

    def __handlePrint(self, message, logger: Logger):
        if logger != None:
            logger.writeToLog(message)
        print(message)

    def validateSettings(self,logger):
        self.__handlePrint("Validating settings...", logger)
        if self.getServerSettings()["maxRAM"] < self.getServerSettings()["minRAM"]:
            self.__handlePrint("Argument minRAM is bigger than maxRAM! Exiting...", logger)
            return False
        if self.getServerSettings()["minRAM"] < 0:
            self.__handlePrint("Argumnet minRAM cannot be smaller or equal than zero!", logger)
            return False
        if self.getServerSettings()["maxRAM"] == self.getServerSettings()["minRAM"]:
            self.__handlePrint("Argument maxRAM has to be bigger than minRAM!", logger)
            return False
        if type(self.getServerSettings()["minRAM"]) != int:
            self.__handlePrint("Argument minRAM has to be an integer!", logger)
            return False
        if type(self.getServerSettings()["maxRAM"]) != int:
            self.__handlePrint("Argument maxRAM has to be an integer!", logger)
            return False
        if self.getBotSettings()["standardChannel"] == "":
            self.__handlePrint("No channel for listening has been set! Exiting...",logger)
            return False
        if self.getBotSettings()["checkRole"] == "":
            self.__handlePrint("No role set for restricted access commands! Exiting...",logger)
        return True

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