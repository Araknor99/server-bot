from datetime import datetime

class Logger:
    def __init__(self,path,printToConsole):
        self.__printToConsole = printToConsole
        self.__path = path
        self.__file = None
        self.writeToLog("Starting the Logger!")

    def writeToLog(self,message):
        self.__file = open(self.__path,"a")

        time = datetime.now()
        timestring = time.strftime("%d/%m/%Y %H:%M:%S") + " - " + message + "\n"
        self.__file.write(timestring)
        if self.__printToConsole:
            print(message)

        self.__file.close()

    def endLog(self):
        self.writeToLog("Closing the log!\n\n")

