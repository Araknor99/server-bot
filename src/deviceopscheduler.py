from sched import scheduler,Event

import time
import datetime

class DeviceOpScheduler:
    def __init__(self):
        self.cOp: str = None
        self.scheduler: scheduler = scheduler(datetime.datetime,time.sleep)
        self.scheduledTime: datetime.datetime = None
        self.timeOfSchedule: datetime.datetime = None
        self.onEventfunc: callable = None

    def setEvent(self,timePoint: datetime.datetime,onEventfunc: callable):
        if self.eventScheduled():
            raise RuntimeError("DeviceOpScheduler does not support adding more than one event!")
        self.timeOfSchedule = datetime.datetime.now()
        self.scheduledTime = timePoint
        self.onEventfunc = onEventfunc
        self.scheduler.enterabs(self.scheduledTime,0,self.onEventfunc)

    def clearEvent(self):
        if not self.eventScheduled():
            raise RuntimeError("Trying to cancel event with no event scheduled!")
        self.scheduler.cancel(self.scheduler.queue[0])
        self.onEventfunc = None
        self.scheduledTime = None
        self.timeOfSchedule = None
        self.cOp = None

    def when(self) -> datetime.datetime:
        return self.scheduledTime

    def howLongTill(self) -> datetime.timedelta:
        if self.scheduledTime == None:
            return None
        return self.scheduledTime - self.timeOfSchedule

    def eventScheduled(self) -> bool:
        if len(self.scheduler.queue) > 0:
            return True
        return False

    def getEventType(self) -> str:
        return self.cOp