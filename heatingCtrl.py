from Modbus import modbus_device

class HeatingCtrl(modbus_device):
    def __init__(self):
        ip ="192.168.0.23"
        port = "502"
        modbus_device.__init__(self,ip,port)
        self.newRegister("SpeicherOben",2,1,False,0.1,"float","°C")
        self.newRegister("SpeicherMitte",5,1,False,0.1,"float","°C")
        self.newRegister("SolarKollektor",7,1,False,0.1,"float","°C")
        self.newRegister("AktuellerVerbrauch",8,1,False,1,"int","W")
        self.newRegister("Heizstab_Ein_nAus",64,1,False,1,"bool","")
        self.newRegister("Heizstab_SollTemp",65,1,False,0.1,"float","°C")
        self.newRegister("Heizstab_Stufe0",66,1,False,1,"bool","")
        self.newRegister("Heizstab_Stufe1",67,1,False,1,"bool","")
        self.newRegister("Heizstab_Stufe2",68,1,False,1,"bool","")
