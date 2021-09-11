import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(threadName)s %(filename)s %(lineno)d: %(message)s', level=logging.INFO)
logger = logging.getLogger(__file__)

import numpy as np
from heatingCtrl import HeatingCtrl
import os
import time
from Heizstab import HeizstabElement
from SMA_SunnyBoy import SMA_SunnyBoy
from SMA_StorageBoy import SMA_StorageBoy
from PowerManager import PowerManager
from BatteryManager import BatteryManager
from MqttClient import MqttClient


abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


from testHeatingCtrl import HeatingCtrl as testHeatingCtrl
from SimulationExamples import SpecificExamplePowerSource

def main():
    mqtt_client = MqttClient("192.168.178.107",1883)
    mqtt_client.topic_prefix = "heating"
    mqtt_client.publish("test")

    test = True

    if not test:
        heatingCtrl = HeatingCtrl()
    else:
        heatingCtrl = testHeatingCtrl()
    maxTemperature = 160

    def read_temperature_sensor():
        return 20

    heizstab0 = HeizstabElement(
        power=500,
        max_time_on=40,#900,
        min_time_on=10,
        min_time_off=60,#1800,
        name="heizstab0",
        thread_period=0.1#120
    )
    heizstab0.external_switch_function = \
        lambda x: heatingCtrl.write_register("Heizstab_Stufe0", int(x))
    heizstab0.read_temperature_sensor = read_temperature_sensor
    heizstab0.temperature_max = maxTemperature
    heizstab0.mqtt_client = mqtt_client

    heizstab1 = HeizstabElement(
        power=750,
        max_time_on=40,#900,
        min_time_on=10,
        min_time_off=60,#1800,
        name="heizstab1",
        thread_period=0.1#120
    )
    heizstab1.external_switch_function = \
        lambda x: heatingCtrl.write_register("Heizstab_Stufe1", int(x))
    heizstab1.read_temperature_sensor = read_temperature_sensor
    heizstab1.temperature_max = maxTemperature
    heizstab1.mqtt_client = mqtt_client

    heizstab2 = HeizstabElement(
        power=1000,
        max_time_on=40,#900,
        min_time_on=10,
        min_time_off=60,#1800,
        name="heizstab2",
        thread_period=0.1#120
    )
    heizstab2.external_switch_function = \
        lambda x: heatingCtrl.write_register("Heizstab_Stufe2", int(x))
    heizstab2.read_temperature_sensor = read_temperature_sensor
    heizstab2.temperature_max = maxTemperature
    heizstab2.mqtt_client = mqtt_client

    heizstäbe = [heizstab0, heizstab1, heizstab2]

    if not test:
        storageBoy = SMA_StorageBoy("192.168.0.147")
        batteryManager = BatteryManager([storageBoy])
        sunnyBoy = SMA_SunnyBoy("192.168.0.140","sunnyBoy-140")
        sources = [batteryManager, sunnyBoy]
        sinks = [*heizstäbe]
    else:
        # storageBoy = SMA_StorageBoy("192.168.178.113")
        # batteryManager = BatteryManager([storageBoy])
        # sunnyBoy = SMA_SunnyBoy("192.168.178.128","sunnyBoy")
        # pikoInverter = Piko_inverter("piko_inverter")
        from sinGen import sinGen
        power_vector, hour_vector  = sinGen(24*10,2010)
        # power_vector = np.ones(len(power_vector))*3100
        # power_vector = [3000,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        #     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        #     3000,3000,3000,3000,3000,3000,3000,3000,3000,
        #     3000,3000,3000,3000,3000,3000,3000,3000,3000,
        #     3000,3000,3000,3000,0,0,0,0,0,0,0,0,0,0,0,0,0]
        # power_vector = [1010] * 240
        sim_source_1 = SpecificExamplePowerSource(name="source1", powers=power_vector)

        class TemperatureExample:
            def __init__(self,length,max):
                self.temp_vector = np.linspace(0,max,length)
                self.counter = 0

            def read(self):
                retVal = self.temp_vector[self.counter]
                self.counter += 1
                return retVal

        temperatureExample0 = TemperatureExample(len(power_vector),120)
        temperatureExample1 = TemperatureExample(len(power_vector),120)
        temperatureExample2 = TemperatureExample(len(power_vector),120)

        heizstab0.read_temperature_sensor = temperatureExample0.read
        heizstab1.read_temperature_sensor = temperatureExample1.read
        heizstab2.read_temperature_sensor = temperatureExample2.read

        # sources = [sim_source_1,batteryManager,sunnyBoy]
        sources = [sim_source_1]
        sinks = [*heizstäbe]

    power_manager = PowerManager(sources,sinks)


    if test:
        from datetime import datetime
        time_vector = []
        data_vector = [[],[],[],[]]
        source_power_vector = []
        allow_vector = [[],[],[],[]]
        status_vector = [[],[],[],[]]
        remain_power_vector = []
        power_dist_vector = []
        temp_vector = []
    run = True
    counter = 0
    while run:
        try:
            remain_power_vector.append(power_manager.distribute())
        except:
            break
        if test:
            import copy
            time.sleep(heizstab0.thread.period*2)
            time_vector.append(datetime.now())
            data_vector[0].append(heatingCtrl.read_value("Heizstab_Stufe0"))
            data_vector[1].append(heatingCtrl.read_value("Heizstab_Stufe1"))
            data_vector[2].append(heatingCtrl.read_value("Heizstab_Stufe2"))
            a = [
                int(heatingCtrl.read_value("Heizstab_Stufe0")),
                int(heatingCtrl.read_value("Heizstab_Stufe1")),
                int(heatingCtrl.read_value("Heizstab_Stufe2"))]
            logger.info(a)
            status_vector[0].append(heizstab0.status[0])
            status_vector[1].append(heizstab1.status[0])
            status_vector[2].append(heizstab2.status[0])
            allow_vector[0].append(heizstab0.allowed_power)
            allow_vector[1].append(heizstab1.allowed_power)
            allow_vector[2].append(heizstab2.allowed_power)
            temp_vector.append(heizstab0.last_read_temperature)
            source_power_vector.append(sim_source_1.power_list[counter])
            power_dist_vector.append(copy.copy(power_manager.power_distribution))
        counter += 1
        time.sleep(1)

    if test:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(5,1,sharex=True)

        ax[0].plot(time_vector,data_vector[0],'-x',label="Heiz0")
        ax[0].plot(time_vector,data_vector[1],'-x',label="Heiz1")
        ax[0].plot(time_vector,data_vector[2],'-x',label="Heiz2")
        ax[0].set_title("on")

        ax[1].plot(time_vector,allow_vector[0],'-x',label="Heiz0")
        ax[1].plot(time_vector,allow_vector[1],'-x',label="Heiz1")
        ax[1].plot(time_vector,allow_vector[2],'-x',label="Heiz2")
        ax[1].set_title("allow_power")

        ax[2].plot(time_vector,status_vector[0],'-x',label="Heiz0")
        ax[2].plot(time_vector,status_vector[1],'-x',label="Heiz1")
        ax[2].plot(time_vector,status_vector[2],'-x',label="Heiz2")
        ax[2].set_title("status")

        ax[3].plot(time_vector,source_power_vector,'-x',label="power")
        ax[3].plot(time_vector,remain_power_vector,'-x',label="remain_power")

        ax[4].plot(time_vector,temp_vector,'-x',label="temperature")

        for i in ax:
            i.legend()
        plt.show()


if __name__ == "__main__":
    main()
