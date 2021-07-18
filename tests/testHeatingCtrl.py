from Modbus import modbus_device

class HeatingCtrl(modbus_device):
    def __init__(self):
        ip = "192.168.178.107"
        port = "502"
        modbus_device.__init__(self,ip,port)
        self.newRegister(name="SpeicherOben",address=2,length=1,signed=False,factor=0.1,type_="float",unit="°C")
        self.newRegister(name="SpeicherMitte",address=5,length=1,signed=False,factor=0.1,type_="float",unit="°C")
        self.newRegister(name="SolarKollektor",address=7,length=1,signed=True,factor=0.1,type_="float",unit="°C")
        self.newRegister(name="AktuellerVerbrauch",address=8,length=1,signed=False,factor=1,type_="int",unit="W")
        self.newRegister(name="Heizstab_Ein_nAus",address=64,length=1,signed=False,factor=1,type_="bool",unit="")
        self.newRegister(name="Heizstab_SollTemp",address=65,length=1,signed=False,factor=0.1,type_="float",unit="°C")
        self.newRegister(name="Heizstab_Stufe0",address=66,length=1,signed=False,factor=1,type_="bool",unit="")
        self.newRegister(name="Heizstab_Stufe1",address=67,length=1,signed=False,factor=1,type_="bool",unit="")
        self.newRegister(name="Heizstab_Stufe2",address=68,length=1,signed=False,factor=1,type_="bool",unit="")
