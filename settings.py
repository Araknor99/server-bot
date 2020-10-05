from pathlib import Path
import os
import json

class SettingsManager:
    def __init__(self):
        self.__onDefaultSettings = False

    def getSettings(self):
        path = "settings.json"
        if not Path(path).is_file():
            path = "defaultSettings.json"
            self.__onDefaultSettings = True
        
        file = open(path,"r")
        text = ""

        for line in file:
            text += line
        file.close()

        return json.loads(text)

    def dumpSettings(self,settings):
        if Path("settings.json").is_file():
            os.remove("settings.json")
        file = open("settings.json","w")
        file.write(json.dumps(settings))
        file.close()

    def onDefaultSettings(self):
        return self.__onDefaultSettings