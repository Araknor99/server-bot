from pathlib import Path
from filehandling import FileHandler
from logger import Logger

class SettingsManager:
    def __init__(self):
        self.__settings = None
        self.__serverSettings = None
        self.__descriptions = None
        self.__onDefaultSettings = False

    def loadSettings(self,fileHandler: FileHandler):
        descriptionPath = "../settings/descriptions.json"
        path = "../settings/settings.json"
        if not Path(path).is_file():
            path = "../settings/defaultSettings.json"
            self.__onDefaultSettings = True

        self.__descriptions = fileHandler.loadJSON(descriptionPath)
        self.__settings = fileHandler.loadJSON(path)
        self.__serverSettings = self.__settings["serverSettings"]

    def interpretArgs(self,argv):
        #Check whether the flags have been set correctly
        #Might change functionality to support flags that need no value set
        #If the function cannot interpret the arguments then it returns False
        for i in range(0,len(argv),2):
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

    #TODO: finish function
    def validateSettings(self):
        if self.__serverSettings["maxRAM"] < self.__serverSettings["minRAM"]:
            print("Argument minRAM is bigger than maxRAM! Exiting...")
            return False
        return True

    def __logSettings(self,logger: Logger,settings,descriptions):
        for key, setting in settings.items():
            if isinstance(setting,dict):
                self.__logSettings(logger,setting,descriptions[key])
            else:
                logger.writeToLog(descriptions[key].format(setting))

    def logSettings(self,logger: Logger):
        if self.__onDefaultSettings:
            logger.writeToLog("No custom settings set! Running on default settings!")
        self.__logSettings(logger,self.__settings,self.__descriptions)

    def getSettings(self):
        return self.__settings

    def getServerSettings(self):
        return self.__serverSettings

    def onDefaultSettings(self):
        return self.__onDefaultSettings