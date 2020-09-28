from datetime import datetime

class Logger:
    def __init__(self,path):
        self.__path = path
        self.__file = None

    def openLog(self):
        self.__file = open(self.__path,"a")
        self.writetolog("Starting the Logger!")

    def writetolog(self,message):
        time = datetime.now()
        timestring = time.strftime("%d/%m/%Y %H:%M:%S") + " - " + message + "\n"
        self.__file.write()

    def closeLog(self):
        self.__file.write("\n\n")
        self.__file.close()

