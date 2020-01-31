import socket
import time
import argparse
import json

tryMQQT = False
debugOn = False

if tryMQQT:
    import os

# Define some fixed types strings 
class HeaterStatus():
    """Heater function status"""
    heaterOn = False
    fanSpeed = 0
    circulationFanOn = False
    manualMode = False
    autoMode = False
    setTemp = 0
    zoneA = False
    zoneB = False
    zoneC = False
    zoneD = False

    def SetMode(self,mode):
        # A = Auto Mode and M = Manual Mode
        if mode == "A":
            self.autoMode = True
            self.manualMode = False
        elif mode == "M":
            self.autoMode = False
            self.manualMode = True

    def SetZones(self,za,zb,zc,zd):
        # Y = On, N = off
        self.zoneA = YNtoBool(za)
        self.zoneB = YNtoBool(zb)
        self.zoneC = YNtoBool(zc)
        self.zoneD = YNtoBool(zd)

    def CirculationFanOn(self,statusStr):
        # Y = On, N = Off
        if statusStr == "Y":
            self.circulationFanOn = True
        else:
            self.circulationFanOn = False

    def Dump(self):
        """Print out the heater status in JSON format.

            "Heater": {
                "HeaterOn":false,
                "FanSpeed":0,
                "CirculationFanOn":false,
                "AutoMode":false,
                "ManualMode":false,
                "SetTemp":0,
                "ZoneA":false,
                "ZoneB":false,
                "ZoneC":false,
                "ZoneD":false
            }

        }
        """
        heaterStatusJson = "\"Heater\": { \"HeaterOn\":" + JsonBool(self.heaterOn) + "," \
            + "\"FanSpeed\": " + str(self.fanSpeed) + "," \
            + "\"CirculationFanOn\": "   + JsonBool(self.circulationFanOn) + "," \
            + "\"AutoMode\": "   + JsonBool(self.autoMode) + "," \
            + "\"ManualMode\": " + JsonBool(self.manualMode) + "," \
            + "\"SetTemp\": " + str(self.setTemp) + "," \
            + "\"ZA\": " + JsonBool(self.zoneA) + "," \
            + "\"ZB\": " + JsonBool(self.zoneB) + "," \
            + "\"ZC\": " + JsonBool(self.zoneC) + "," \
            + "\"ZD\": " + JsonBool(self.zoneD) + "}"

        return heaterStatusJson

class CoolingStatus():
    """Cooling function status"""
    coolingOn = False
    circulationFanOn = False
    manualMode = False
    autoMode = False
    setTemp = 0
    zoneA = False
    zoneB = False
    zoneC = False
    zoneD = False

    def SetMode(self,mode):
        # A = Auto Mode and M = Manual Mode
        if mode == "A":
            self.autoMode = True
            self.manualMode = False
        elif mode == "M":
            self.autoMode = False
            self.manualMode = True

    def SetZones(self,za,zb,zc,zd):
        # Y = On, N = off
        self.zoneA = YNtoBool(za)
        self.zoneB = YNtoBool(zb)
        self.zoneC = YNtoBool(zc)
        self.zoneD = YNtoBool(zd)

    def CirculationFanOn(self,statusStr):
        # Y = On, N = Off
        if statusStr == "Y":
            self.circulationFanOn = True
        else:
            self.circulationFanOn = False

    def Dump(self):
        """Print out the cooling status in JSON format.

            "Cooling": {
                "CoolingOn":false,
                "CirculationFanOn":false,
                "AutoMode":false,
                "ManualMode":false,
                "SetTemp":0,
                "ZA":false,
                "ZB":false,
                "ZC":false,
                "ZD":false
            }

        }
        """
        coolingStatusJson = "\"Cooling\": { \"CoolingOn\":" + JsonBool(self.coolingOn) + "," \
            + "\"CirculationFanOn\": "   + JsonBool(self.circulationFanOn) + "," \
            + "\"AutoMode\": "   + JsonBool(self.autoMode) + "," \
            + "\"ManualMode\": " + JsonBool(self.manualMode) + "," \
            + "\"SetTemp\": " + str(self.setTemp) + "," \
            + "\"ZA\": " + JsonBool(self.zoneA) + "," \
            + "\"ZB\": " + JsonBool(self.zoneB) + "," \
            + "\"ZC\": " + JsonBool(self.zoneC) + "," \
            + "\"ZD\": " + JsonBool(self.zoneD) + "}"

        return coolingStatusJson

class EvapStatus():
    """Evap function status"""
    evapOn = False
    fanOn = False
    fanSpeed = 0
    waterPumpOn = False

    def FanOn(self,statusStr):
        # N = On, F = Off
        if statusStr == "N":
            self.fanOn = True
        else:
            self.fanOn = False

    def FanSpeed(self,speedInt):
        self.fanSpeed = speedInt

    def WaterPumpOn(self,statusStr):
        # N = On, F = Off
        if statusStr == "N":
            self.waterPumpOn = True
        else:
            self.waterPumpOn = False

    def Dump(self):
        """Print out the EVAP status in JSON format.

            "Evap":{
                "EvapOn": false,
                "FanOn": false,
                "FanSpeed": 0,
                "WaterPumpOn":false
            }
        """
        evapStatusJson = "\"Evap\": { \"EvapOn\":" + JsonBool(self.evapOn) + "," \
            + "\"FanOn\": " + JsonBool(self.fanOn) + "," \
            + "\"FanSpeed\": " + str(self.fanSpeed) + "," \
            + "\"WaterPumpOn\": " + JsonBool(self.waterPumpOn) + "}"

        return evapStatusJson

class BrivisStatus():
    """Overall Class for describing status"""
    evapMode = False
    coolingMode = False
    heaterMode = False
    systemOn = False
    heaterStatus = HeaterStatus()
    coolingStatus = CoolingStatus()
    evapStatus = EvapStatus()
    
    def setMode(self,mode):
        self.currentMode = mode
        if mode == Mode.HEATING:
            self.heaterMode = True
            self.coolingMode = False
            self.evapMode = False
        elif mode == Mode.COOLING:
            self.heaterMode = False
            self.coolingMode = True
            self.evapMode = False
        elif mode == Mode.EVAP:
            self.heaterMode = False
            self.coolingMode = False
            self.evapMode = True

    def Dump(self):
        """Print out the overall status in JSON format.
        {"Status": {
            "System": {
                "CoolingMode": false,                
                "EvapMode": false,
                "HeaterMode": false,
                "SystemOn": false
            },
            "Heater": {
                "HeaterOn":false,
                "FanSpeed":0,
                "OperatingMode":"manual",
                "SetTemp":0
            },
            "Evap":{
                "EvapOn": false,
                "FanOn": false,
                "FanSpeed": 0,
                "WaterPumpOn":false
            }
        }
        """
        # Don't dump info for non-active modes. e.g If we are in Heater Mode, dump heater info only etc
        sysStatusJson = "{\"Status\": { \"System\": { " \
            + "\"CoolingMode\":"  + JsonBool(self.coolingMode) + "," \
            + "\"CurrentMode\":\""  + ReadableMode(self.currentMode) + "\"," \
            + "\"EvapMode\":"  + JsonBool(self.evapMode) + "," \
            + "\"HeaterMode\":"  + JsonBool(self.heaterMode) + "," \
            + "\"SystemOn\": " + JsonBool(self.systemOn) + " },"

        if self.heaterMode:
            sysStatusJson = sysStatusJson + self.heaterStatus.Dump()
        elif self.coolingMode:
            sysStatusJson = sysStatusJson + self.coolingStatus.Dump()
        elif self.evapMode:
            sysStatusJson = sysStatusJson + self.evapStatus.Dump()
            
        sysStatusJson = sysStatusJson + "}}"

        return sysStatusJson

def JsonBool(bool):
    """Convert python bool to JSON bool"""
    if bool:
        return "true"
    else:
        return "false"

def YNtoBool(str):
    """Convert Rinnai YN to Bool"""
    if str == "Y":
        return True
    else:
        return False

# Ideally we could create an enum, but looks like that needs enum library - which nmight not be
# available???
class Mode:
    HEATING = 1
    EVAP = 2
    COOLING = 3
    RC = 4
    NONE = 5

def ReadableMode(mode):
    if mode == 1:
        return "HEATING"
    elif mode == 2:
        return "EVAP"
    elif mode == 3:
        return "COOLING"
    elif mode == 4:
        return "RC"
    else:
        return "NONE"

# Some nice globals
currentMode = Mode.NONE
status = BrivisStatus()

# Command line parsing
parser = argparse.ArgumentParser()
parser.add_argument("hostIP", help='Rinnai Touch Host IP address')

args = parser.parse_args()


def debugPrint(text):
    if (debugOn):
        print(text)

# Touch Box IP address
touchIP = args.hostIP
touchPort = 27847

def ConnectToTouch(touchIP, port):
    # connect the client
    # create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    debugPrint("Connecting ...")
    client.connect((touchIP, port))
    return client

def GetAttribute(data, attribute, defaultValue):
    return data.get(attribute) or defaultValue

def HandleHeatingMode(client,j,brivisStatus):
    brivisStatus.setMode(Mode.HEATING)

    debugPrint("We are in HEAT mode")

    oop = GetAttribute(j[1].get("HGOM"),"OOP",None)
    if not oop:
        # Probably an error
        debugPrint("No OOP - Not happy, Jan")

    else:
        switch = GetAttribute(oop,"ST",None)
        if switch == "N":
            debugPrint("Heater is ON")
            brivisStatus.systemOn = True
            brivisStatus.heaterStatus.heaterOn = True

            # Heater is on - get attributes
            fanSpeed = GetAttribute(oop,"FL",None)
            debugPrint("Fan Speed is: {}".format(fanSpeed))
            brivisStatus.heaterStatus.fanSpeed = int(fanSpeed) # Should catch errors!

            # Heater is on - get attributes
            circFan = GetAttribute(oop,"CF",None)
            debugPrint("Circulation Fan is: {}".format(circFan))
            brivisStatus.heaterStatus.CirculationFanOn(circFan)

            # GSO should be there
            gso = GetAttribute(j[1].get("HGOM"),"GSO",None)
            if not gso:
                # Probably an error
                debugPrint("No GSO when heater on. Not happy, Jan")
            else:
                # Heater is on - get attributes
                opMode = GetAttribute(gso,"OP",None)
                debugPrint("Heat OpMode is: {}".format(opMode)) # A = Auto, M = Manual
                brivisStatus.heaterStatus.SetMode(opMode)

                # Set temp?
                setTemp = GetAttribute(gso,"SP",None)
                debugPrint("Heat set temp is: {}".format(setTemp))
                brivisStatus.heaterStatus.setTemp = int(setTemp)

        elif switch == "F":
            # Heater is off
            debugPrint("Heater is OFF")
            brivisStatus.systemOn = False
            brivisStatus.heaterStatus.heaterOn = False

        za = zb = zc = zd = None
        z = GetAttribute(j[1].get("HGOM"),"ZAO",None)
        if z:
            za = GetAttribute(z,"UE",None)
        z = GetAttribute(j[1].get("HGOM"),"ZBO",None)
        if z:
            zb = GetAttribute(z,"UE",None)
        z = GetAttribute(j[1].get("HGOM"),"ZCO",None)
        if z:
            zc = GetAttribute(z,"UE",None)
        z = GetAttribute(j[1].get("HGOM"),"ZDO",None)
        if z:
            zd = GetAttribute(z,"UE",None)
        brivisStatus.heaterStatus.SetZones(za,zb,zc,zd)

def HandleCoolingMode(client,j,brivisStatus):
    brivisStatus.setMode(Mode.COOLING)

    debugPrint("We are in COOL mode")

    gss = GetAttribute(j[1].get("CGOM"),"GSS",None)
    if not gss:
        debugPrint("No GSO here")

    else:
        switch = GetAttribute(gss,"CC",None)
        if switch == "Y":
            debugPrint("Cooling is ON")
            brivisStatus.systemOn = True
            brivisStatus.coolingStatus.coolingOn = True

            # Cooling is on - get attributes
            circFan = GetAttribute(gss,"FS",None)
            debugPrint("Circulation Fan is: {}".format(circFan))
            brivisStatus.coolingStatus.CirculationFanOn(circFan)

            # GSO should be there
            gso = GetAttribute(j[1].get("CGOM"),"GSO",None)
            if not gso:
                # Probably an error
                debugPrint("No GSO when cooling on. Not happy, Jan")
            else:
                # Heater is on - get attributes
                opMode = GetAttribute(gso,"OP",None)
                debugPrint("Cooling OpMode is: {}".format(opMode)) # A = Auto, M = Manual
                brivisStatus.coolingStatus.SetMode(opMode)

                # Set temp?
                setTemp = GetAttribute(gso,"SP",None)
                debugPrint("Cooling set temp is: {}".format(setTemp))
                brivisStatus.coolingStatus.setTemp = int(setTemp)

        elif switch == "N":
            # Heater is off
            debugPrint("Cooling is OFF")
            brivisStatus.systemOn = False
            brivisStatus.coolingStatus.coolingOn = False

        za = zb = zc = zd = None
        z = GetAttribute(j[1].get("CGOM"),"ZAO",None)
        if z:
            za = GetAttribute(z,"UE",None)
        z = GetAttribute(j[1].get("CGOM"),"ZBO",None)
        if z:
            zb = GetAttribute(z,"UE",None)
        z = GetAttribute(j[1].get("CGOM"),"ZCO",None)
        if z:
            zc = GetAttribute(z,"UE",None)
        z = GetAttribute(j[1].get("CGOM"),"ZDO",None)
        if z:
            zd = GetAttribute(z,"UE",None)
        brivisStatus.coolingStatus.SetZones(za,zb,zc,zd)

def HandleEvapMode(client,j,brivisStatus):
    brivisStatus.setMode(Mode.EVAP)
    debugPrint("We are in EVAP mode")
    gso = GetAttribute(j[1].get("ECOM"),"GSO",None)
    if not gso:
        debugPrint("No GSO here")
    else:
        debugPrint("Looking at: {}".format(gso))
        switch = GetAttribute(gso,"SW",None)
        if switch == "N":
            # Evap is on - what is the fan speed
            debugPrint("EVAP is ON")
            brivisStatus.systemOn = True
            brivisStatus.evapStatus.evapOn = True

            evapFan = GetAttribute(gso,"FS",None)
            debugPrint("Fan is: {}".format(evapFan))
            brivisStatus.evapStatus.FanOn(evapFan)
            
            fanSpeed = GetAttribute(gso,"FL",None)
            debugPrint("Fan Speed is: {}".format(fanSpeed))
            brivisStatus.evapStatus.FanSpeed(int(fanSpeed))

            waterPump = GetAttribute(gso,"PS",None)
            debugPrint("Water Pump is: {}".format(waterPump))
            brivisStatus.evapStatus.WaterPumpOn(waterPump)


        elif switch == "F":
            # Evap is off
            debugPrint("EVAP is OFF")
            brivisStatus.systemOn = False
            brivisStatus.evapStatus.evapOn = False

def HandleStatus(client,brivisStatus):
    # Make sure enough time passed to get a status message
    time.sleep(1)
    status = client.recv(4096)
    debugPrint(status)

    jStr = status[14:]
    debugPrint(jStr)

    j = json.loads(jStr)
    debugPrint(json.dumps(j, indent = 4))

    if 'HGOM' in j[1]:
        HandleHeatingMode(client,j,brivisStatus)

    elif 'CGOM' in j[1]:
        HandleCoolingMode(client,j,brivisStatus)

    elif 'ECOM' in j[1]:
        HandleEvapMode(client,j,brivisStatus)

    else:
        debugPrint("Unknown mode")


def main():
    client = ConnectToTouch(touchIP,touchPort)
    brivisStatus = BrivisStatus()
    HandleStatus(client,brivisStatus)
    statusJsonStr = brivisStatus.Dump()
    if tryMQQT:
        # This doesn't actually work - (no access to mosquitto?)
        os.system("mosquitto_pub -h 192.168.1.30 -p 1883 -u xx -P xx -t homeassistant/brivis/status -m \"{}\"".format(statusJsonStr))
    else:
        print(statusJsonStr)


    client.close()

if __name__== "__main__":
  main()