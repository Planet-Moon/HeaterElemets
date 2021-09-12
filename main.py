import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(threadName)s %(filename)s %(lineno)d: %(message)s', level=logging.INFO)
logger = logging.getLogger(__file__)

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


def main():
    mqtt_client = MqttClient("192.168.0.23",1883)
    mqtt_client.topic_prefix = "heating"

    heatingCtrl = HeatingCtrl()
    maxTemperature = 60

    def read_temperature_sensor():
        return heatingCtrl.read_value("SpeicherOben")

    heizstab0 = HeizstabElement(
        power=1000,
        max_time_on=10800, # 3h
        min_time_on=900, # 15 min
        min_time_off=1200, # 20 min
        name="heizstab0",
        thread_period=1  # 120
    )
    heizstab0.external_switch_function = \
        lambda x: heatingCtrl.write_register("Heizstab_Stufe0", int(x))
    heizstab0.read_temperature_sensor = read_temperature_sensor
    heizstab0.temperature_max = maxTemperature
    heizstab0.mqtt_client = mqtt_client

    heizstab1 = HeizstabElement(
        power=1000,
        max_time_on=10800, # 3h
        min_time_on=900, # 15 min
        min_time_off=1200, # 20 min
        name="heizstab1",
        thread_period=1  # 120
    )
    heizstab1.external_switch_function = \
        lambda x: heatingCtrl.write_register("Heizstab_Stufe1", int(x))
    heizstab1.read_temperature_sensor = read_temperature_sensor
    heizstab1.temperature_max = maxTemperature
    heizstab1.mqtt_client = mqtt_client

    heizstab2 = HeizstabElement(
        power=1000,
        max_time_on=10800, # 3h
        min_time_on=900, # 15 min
        min_time_off=1200, # 20 min
        name="heizstab2",
        thread_period=1  # 120
    )
    heizstab2.external_switch_function = \
        lambda x: heatingCtrl.write_register("Heizstab_Stufe2", int(x))
    heizstab2.read_temperature_sensor = read_temperature_sensor
    heizstab2.temperature_max = maxTemperature
    heizstab2.mqtt_client = mqtt_client

    heizstäbe = [heizstab0, heizstab1, heizstab2]

    storageBoy = SMA_StorageBoy("192.168.0.147")
    batteryManager = BatteryManager([storageBoy])
    sunnyBoy = SMA_SunnyBoy("192.168.0.140", "sunnyBoy-140")
    sources = [batteryManager, sunnyBoy]
    sinks = [*heizstäbe]

    power_manager = PowerManager(sources, sinks)
    power_manager.power_grid = lambda: storageBoy.LeistungBezug - storageBoy.LeistungEinspeisung

    run = True
    logger.info("Running")
    while run:
        try:
            power_manager.distribute()
        except:
            break
        time.sleep(60)


if __name__ == "__main__":
    main()
