from pathlib import Path
import os
import json

class FileHandler:
    def loadJSON(self,path):
        file = open(path)
        text = ""
        
        for line in file:
            text += line
        file.close()

        return json.loads(text)

    def dumpJSON(self,path,content):
        if Path(path).is_file():
            os.remove(path)
        os.system("touch {}".format(path))
        file = open(path,"w")
        file.write(json.dumps(content))
        file.close()

    def getToken(self,path):
        file = open(path)
        content = file.read()
        file.close()
        return content