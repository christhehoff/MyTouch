import socket
import time
import argparse
import json
#import enum

# Define some fixed types strings 

# Rather than loading enum libraru
class Mode:
    HEATING = 1
    EVAP = 2
    COOLING = 3
    RC = 4
    NONE = 5
    
currentMode = Mode.NONE

# Top level mode
# Operating mode
modeCoolCmd = 'N000001{"SYST": {"OSS": {"MD": "C" } } }'
modeEvapCmd = 'N000001{"SYST": {"OSS": {"MD": "E" } } }'
modeHeatCmd = 'N000001{"SYST": {"OSS": {"MD": "H" } } }'

# Heating Commands
#heatCmd = 'N000001{"HGOM": {"OOP": {"ST": "{}" } } }' # N = On, F = Off
heatOnCmd = 'N000001{"HGOM": {"OOP": {"ST": "N" } } }'
heatOffCmd = 'N000001{"HGOM": {"OOP": {"ST": "F" } } }'

heatSetTemp = 'N000001{{"HGOM": {{"GSO": {{"SP": "{temp}" }} }} }}'
heatCircFanOn = 'N000001{"HGOM": {"OOP": {"ST": "Z" } } }'

#heatZone = 'N000001{"HGOM": {"Z{zone}O": {"UE": "{}" } } }'  # Y = On, N = Off
heatZoneOn = 'N000001{{"HGOM": {{"Z{zone}O": {{"UE": "Y" }} }} }}'
heatZoneOff = 'N000001{{"HGOM": {{"Z{zone}O": {{"UE": "N" }} }} }}'
heatZoneA = 'N000001{"HGOM": {"ZAO": {"UE": "{}" } } }'  # Y = On, N = Off
heatZoneB = 'N000001{"HGOM": {"ZBO": {"UE": "{}" } } }'
heatZoneC = 'N000001{"HGOM": {"ZCO": {"UE": "{}" } } }'
heatZoneD = 'N000001{"HGOM": {"ZDO": {"UE": "{}" } } }'

# Cooling Commands
#coolCmd = 'N000001{"CGOM": {"OOP": {"ST": "{}" } } }' # N = On, F = Off
coolOnCmd = 'N000001{"CGOM": {"OOP": {"ST": "N" } } }'
coolOffCmd = 'N000001{"CGOM": {"OOP": {"ST": "F" } } }'

coolSetTemp = 'N000001{{"CGOM": {{"GSO": {{"SP": "{temp}" }} }} }}'
coolCircFanOn = 'N000001{"CGOM": {"GSO": {"FS": "M" } } }'

#coolZone = 'N000001{"HGOM": {"Z{zone}O": {"UE": "{}" } } }'  # Y = On, N = Off
coolZoneOn = 'N000001{{"CGOM": {{"Z{zone}O": {{"UE": "Y" }} }} }}'
coolZoneOff = 'N000001{{"CGOM": {{"Z{zone}O": {{"UE": "N" }} }} }}'
coolZoneA = 'N000001{"CGOM": {"ZAO": {"UE": "{}" } } }'  # Y = On, N = Off
coolZoneB = 'N000001{"CGOM": {"ZBO": {"UE": "{}" } } }'
coolZoneC = 'N000001{"CGOM": {"ZCO": {"UE": "{}" } } }'
coolZoneD = 'N000001{"CGOM": {"ZDO": {"UE": "{}" } } }'

# Evap Cooling commands
#evapCmd =  'N000001{"ECOM": {"GSO": {"SW": "{}" } } }' # N = On, F = Off
evapOnCmd =  'N000001{"ECOM": {"GSO": {"SW": "N" } } }'
evapOffCmd =  'N000001{"ECOM": {"GSO": {"SW": "F" } } }'

#evapPumpCmd = 'N000001{"ECOM": {"GSO": {"PS": "{}" } } }' # N = On, F = Off
evapPumpOn = 'N000001{"ECOM": {"GSO": {"PS": "N" } } }'
evapPumpOff = 'N000001{"ECOM": {"GSO": {"PS": "F" } } }'

#evapFanCmd = 'N000014{"ECOM": {"GSO": {"FS": "{}" } } }' # N = On, F = Off
evapFanOn = 'N000014{"ECOM": {"GSO": {"FS": "N" } } }'
evapFanOff = 'N000014{"ECOM": {"GSO": {"FS": "F" } } }'
evapFanSpeed = 'N000001{{"ECOM": {{"GSO": {{"FL": "{speed}" }} }} }}' # 1 - 16

# Command line parsing
parser = argparse.ArgumentParser()
parser.add_argument("hostIP", help='Rinnai Touch Host IP address')

# Must be one of these
parser.add_argument("--mode",choices=['heat','evap','cool','rc','status'], help='What function are we acting on')
parser.add_argument("--action",choices=['on','off'], help='What are we doing to the mode')

parser.add_argument("--heatTemp",type=int,choices=range(20,30))
parser.add_argument("--heatZone",choices=['A','B','C','D'], help='Which Zone?')
parser.add_argument("--zoneAction",choices=['on','off'], help='What are we doing to the zone')
parser.add_argument("--heatFan",choices=['on','off'], help='Turn the Heater circulation fan on/off')

parser.add_argument("--coolTemp",type=int,choices=range(8,30))
parser.add_argument("--coolZone",choices=['A','B','C','D'], help='Which Zone?')
parser.add_argument("--coolFan",choices=['on','off'], help='Turn the Cooling circulation fan on/off')

parser.add_argument("--evapFanSpeed",type=int,choices=range(1,16))
parser.add_argument("--evapPump",choices=['on','off'], help='Turn the Evap pump on/off')
parser.add_argument("--evapFan",choices=['on','off'], help='Turn the Evap fan on/off')

args = parser.parse_args()

debugOn = True

def debugPrint(text):
    if (debugOn):
        print(text)


debugPrint(args)

# Touch Box IP address
port = 27847
touchIP = args.hostIP

# create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client
debugPrint("Connecting ...")
client.connect((touchIP, port))


def SendToTouch(client,cmd):
    """Send the command and return the response."""
    debugPrint("DEBUG: {}".format(cmd))
    response = "NA"
    client.send(cmd.encode())
    # Let that sink in
    time.sleep(0.5)
    response = client.recv(4096)
    return response

def HandleHeat(args,client,currentMode):
    # Make sure we are in heater mode
    if currentMode != Mode.HEATING:
        resp = SendToTouch(client,modeHeatCmd)
        debugPrint(resp)

    # Give it a chance if there are further commands
    time.sleep(0.5)

    if args.action is not None:
        if args.action == "on":
            resp = SendToTouch(client,heatOnCmd)
            debugPrint(resp)
        else:
            # Assume it is off cmd then
            # Assume we are in heater mode, otherwise no need to turn it Off
            resp = SendToTouch(client,heatOffCmd)
            debugPrint(resp)
            return

    if args.heatTemp is not None:
        # Assume on already
        resp = SendToTouch(client,heatSetTemp.format(temp=args.heatTemp))
        debugPrint(resp)

    if args.heatZone is not None:
        if args.zoneAction == "on":
            # Assume on already
            resp = SendToTouch(client,heatZoneOn.format(zone=args.heatZone))
            debugPrint(resp)
        elif args.zoneAction == "off":
            resp = SendToTouch(client,heatZoneOff.format(zone=args.heatZone))
            debugPrint(resp)
            return

def HandleCool(args,client,currentMode):

        # Make sure we are in cooling mode
    if currentMode != Mode.COOLING:
        resp = SendToTouch(client,modeCoolCmd)
        debugPrint(resp)

    # Give it a chance if there are further commands
    time.sleep(0.5)

    if args.action is not None:
        if args.action == "on":
            resp = SendToTouch(client,coolOnCmd)
            debugPrint(resp)
        else:
            # Assume it is off cmd then
            # Assume we are in cooling mode, otherwise no need to turn it Off
            resp = SendToTouch(client,coolOffCmd)
            debugPrint(resp)
            return
    
    if args.coolTemp is not None:
        time.sleep(2)
        # Assume on already
        resp = SendToTouch(client,coolSetTemp.format(temp=args.coolTemp))
        debugPrint(resp)

    if args.coolZone is not None:
        time.sleep(2)
        
        if args.zoneAction == "on":
            # Assume on already
            resp = SendToTouch(client,coolZoneOn.format(zone=args.coolZone))
            debugPrint(resp)
        elif args.zoneAction == "off":
            resp = SendToTouch(client,coolZoneOff.format(zone=args.coolZone))
            debugPrint(resp)
            return


def HandleEvap(args,client,currentMode):
    # Make sure we are in evap mode
    if currentMode != Mode.EVAP:
        resp = SendToTouch(client,modeEvapCmd)
        debugPrint(resp)

    # Give it a chance
    time.sleep(0.5)

    if args.action is not None:
        if args.action == "on":

            resp = SendToTouch(client,evapOnCmd)
            debugPrint(resp)
        else:
            # Assume it is off cmd then
            # Assume we are in heater mode, otherwise no need to turn it Off
            resp = SendToTouch(client,evapOffCmd)
            debugPrint(resp)
            return

    if args.evapFanSpeed is not None:
        resp = SendToTouch(client,evapFanSpeed.format(speed=args.evapFanSpeed))
        debugPrint(resp)

    if args.evapFan is not None:
        if args.evapFan == "on":
            resp = SendToTouch(client,evapFanOn)
            debugPrint(resp)
        else:
            # Assume off cmd then
            resp = SendToTouch(client,evapFanOff)
            debugPrint(resp)

def HandleMode(args,client):
    """Process setting mode and its state."""
    # Get the current status first
    currentMode = HandleStatus(args,client)

    if args.mode == "heat":
        HandleHeat(args,client, currentMode)

    elif args.mode =="evap":
        HandleEvap(args,client,currentMode)

    elif args.mode =="cool":
        HandleEvap(args,client,currentMode)

    elif args.mode =="status":
        # Get the current status
        HandleStatus(args,client)

    else:
            debugPrint("Not implemented yet")

def HandleStatus(args,client):
    # Make sure enough time passed to get a status message
    time.sleep(1)
    status = client.recv(4096)
    debugPrint(status)

    jStr = status[14:]
    debugPrint(jStr)

    j = json.loads(jStr)
    debugPrint(json.dumps(j, indent = 4))

    if 'HGOM' in j[1]:
        currentMode = Mode.HEATING
        debugPrint("We are in HEATING mode")
        # debugPrint(j[1]['HGOM'])
    elif 'ECOM' in j[1]:
        currentMode = Mode.EVAP
        debugPrint("We are in EVAP mode")
    elif 'CGOM' in j[1]:
        currentMode = Mode.COOLING
        debugPrint("We are in COOLING mode")    
    else:
        debugPrint("Unknown mode")

    return currentMode

if args.mode is not None:
    if args.mode == "status":
        currentMode = HandleStatus(args,client)
    else:
        HandleMode(args,client)
else:
    exit()

client.close()