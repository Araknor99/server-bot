from datetime import datetime

class Logger:
    def __init__(self,path,printToConsole):
        self.__printToConsole = printToConsole
        self.__path = path
        self.__file = None
        self.writeToLog("Starting the Logger!")

    #Opening and closing the file in the function so the log gets updated immediatly
    def writeToLog(self,message):
        self.__file = open(self.__path,"a")

        time = datetime.now()
        timestring = time.strftime("%d/%m/%Y %H:%M:%S") + " - " + message + "\n"
        self.__file.write(timestring)
        if self.__printToConsole:
            print(message)

        self.__file.close()

    #"Closing" the log
    #Just to add a divide between the end of the current log and the beggining of the next log
    def endLog(self):
        self.writeToLog("Closing the log!\n\n")

