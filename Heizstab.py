from datetime import timedelta, datetime
import threading
import time
import logging

from PowerSink import PowerSink

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s')
logger = logging.getLogger(__name__)

class HeizstabElement_Thread(threading.Thread):
    def __init__(self,heizstab,period=30,name=""):
        self.heizstab = heizstab
        if name:
            name = name
        else:
            name = self.heizstab.name+"_thread"
        threading.Thread.__init__(self, name=name)
        self.period = period
        self.enabled = True

    def run(self):
        while self.enabled:
            time_now = datetime.now()
            if self.heizstab.on and time_now > self.heizstab.time_turn_on + self.heizstab.max_time_on:
                self.heizstab.turn_off()

            if time_now <= self.heizstab.time_turn_off + self.heizstab.min_time_off:
                self.heizstab.status = (1,"cool down")
            elif time_now <= self.heizstab.time_turn_on + self.heizstab.min_time_on:
                self.heizstab.status = (2,"min time on")
            else:
                self.heizstab.status = (0,"ok")
            time.sleep(self.period)

class HeizstabElement(PowerSink):
    def __init__(self,
        power=1000,
        min_time_on=15,
        max_time_on=30,
        min_time_off=30,
        max_time_off=0,
        name="HeizstabElement",
        thread_period=30):
        PowerSink.__init__(self, name=name)
        self.request_power = power
        self.allowed_power = 0
        self.status = (0,"ok")
        self.min_time_on =  timedelta(seconds=min_time_on)
        self.max_time_on =  timedelta(seconds=max_time_on)
        self.min_time_off = timedelta(seconds=min_time_off)
        self.max_time_off =  timedelta(seconds=max_time_off)
        self._on = False
        self.time_turn_on = datetime(1900,1,1)
        self.time_turn_off = datetime(1900,1,1)
        self.thread = HeizstabElement_Thread(self,period=thread_period)
        self.thread.start()
        self.external_switch_function = lambda value: value
        self.read_temperature_sensor = lambda: 20
        self.last_read_temperature = 0
        self.temperature_max = 50
        self._mqtt_client = None

    @property
    def mqtt_client(self):
        return self._mqtt_client

    @mqtt_client.setter
    def mqtt_client(self,object_):
        self._mqtt_client = object_
        self.mqtt_client.publish(topic=self.name+"/on",payload=str(self.on),retain=True)
        self.mqtt_client.publish(topic=self.name+"/power",payload=str(self.allowed_power),retain=True)


    @property
    def using_power(self):
        return self.allowed_power * self.on

    @property
    def on(self) -> bool:
        return self._on

    @on.setter
    def on(self,value:bool):
        self.external_switch_function(int(value)*10)
        if self.mqtt_client:
            self._mqtt_client.publish(topic=self.name+"/on",payload=str(value),retain=True)
        self._on = value

    def turn_on(self) -> bool:
        time_condition = datetime.now() > self.time_turn_off + self.min_time_off
        if time_condition:
            if not self.on:
                self.time_turn_on = datetime.now()
                self.on = True
                logger.info("Switched on")
            else:
                logger.info("Already on")
            return True
        logger.info("blocked by cool down")
        return False

    def turn_off(self) -> bool:
        time_now = datetime.now()
        if time_now > self.time_turn_on + self.min_time_on:
            if self.on:
                self.time_turn_off = datetime.now()
                self.on = False
                self.allowed_power = 0
                logger.info("Switched off")
            else:
                logger.info("Already off")
            return True
        logger.info("blocked by min time on")
        return False

    def allow_power(self,power=0.0) -> bool:
        retval = None
        power_condition = power >= self.request_power.min
        self.last_read_temperature = self.read_temperature_sensor()
        temperature_condition = self.last_read_temperature < self.temperature_max
        if power_condition and temperature_condition:
            retval = self.turn_on()
            state = "turn on"
        else:
            retval = self.turn_off()
            state = "turn off"
        if retval:
            if self.allowed_power != power:
                self._mqtt_client.publish(topic=self.name+"/power",payload=str(power),retain=True)
            self.allowed_power = power
        return retval

def heizer_enable(value:bool):
    print("enable heizer: "+str(value))

def main():
    heizstabElement = HeizstabElement(min_time_on=10, max_time_on=15,min_time_off=10,thread_period=30)
    # heizstabElement.external_switch_function = heizer_enable
    while True:
        if heizstabElement.on:
            heizstabElement.allow_power(0)
        else:
            heizstabElement.allow_power(1000)
        time.sleep(0.1)

if __name__ == "__main__":
    main()
