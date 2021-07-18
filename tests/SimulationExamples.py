import random
from typing import Counter
from PowerSource import PowerSource
from PowerSink import PowerSink


class ExamplePowerSource(PowerSource):
    def __init__(self, name: str,power_min=5000,power_max=6000):
        super(ExamplePowerSource, self).__init__(name)
        self.power_min = power_min
        self.power_max = power_max

    @property
    def power(self):
        return random.randint(self.power_min, self.power_max)


class SpecificExamplePowerSource(PowerSource):
    def __init__(self, name: str,powers=[]):
        super(SpecificExamplePowerSource, self).__init__(name)
        self.power_list = powers
        self.counter = 0

    @property
    def power(self):
        if self.counter+1 > len(self.power_list):
            raise ValueError("No more entries in power list!")
        retVal = self.power_list[self.counter]
        self.counter += 1
        return retVal


class ExamplePowerSink(PowerSink):
    def __init__(self, name: str):
        super(ExamplePowerSink, self).__init__(name)
        self.request_power = (random.randint(0, 2000), random.randint(2000, 4000))

    def allow_power(self,power:float=0.0) -> bool:
        rand = random.randint(0,9)
        if rand > 5 or True:
            self._allowed_power = power
            return True
        else:
            return False


class ExampleSink(PowerSink):
    def __init__(self, name: str):
        super().__init__(name=name)
