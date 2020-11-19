import time
import datetime
import threading
import sys

class DeviceOpScheduler:
    def __init__(self):
        self.cOp: str = ""
        self.scheduledTime: datetime.datetime = None
        self.timeOfSchedule: datetime.datetime = None
        self.onEventfunc: callable = None
        self.__timeThread: threading.Thread = None

    def setEvent(self, time: datetime.datetime, funcToCall: callable, type: str):
        self.cOp = type
        self.scheduledTime = time
        self.timeOfSchedule = datetime.datetime.now()
        self.onEventfunc = funcToCall
        self.__runTimeThread()

    def stopScheduledOp(self):
        self.__clearEvent()
        self.__stopThread()

    def __clearEvent(self):
        self.cOp = None
        self.scheduledTime = None
        self.timeOfSchedule = None
        self.onEventfunc = None

    def __stopThread(self):
        self.__timeThread.do_run = False
        self.__timeThread = None

    def __runTimeThread(self):
        self.__timeThread = threading.Thread(target=self.__loopFunc)
        self.__timeThread.start()

    def __execFunc(self):
        self.onEventfunc()
        self.__clearEvent()
        self.__timeThread = None

    def __loopFunc(self):
        while True:
            t = threading.current_thread()
            shouldStop = getattr(t,"do_run", False)
            if shouldStop:
                break
            
            scheduledTime = datetime.datetime.now()
            if scheduledTime >= self.scheduledTime:
                self.__execFunc()
                break

            time.sleep(0.5)

        self.__timeThread = None
        sys.exit(0)

    def eventScheduled(self) -> bool:
        return bool(self.__timeThread)

    def getScheduledTime(self) -> datetime.datetime:
        return self.scheduledTime

    def getTimeOfSchedule(self) -> datetime.datetime:
        return self.timeOfSchedule

    def howLongTill(self) -> datetime.timedelta:
        if not self.eventScheduled():
            return None
        
        return self.scheduledTime - datetime.datetime.now()

    def getEventType(self):
        return self.cOp