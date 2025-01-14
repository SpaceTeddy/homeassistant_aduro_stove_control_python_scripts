#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------

#---import
from pyduro.actions import FUNCTIONS, STATUS_PARAMS, discover, get, set, raw
import paho.mqtt.client as mqtt
import asyncio

import json
import time
from datetime import date, timedelta

# ------------------------------------------------------------------------------
# Get data from Home Assistant

MQTT_SERVER_IP   = data.get('MQTT_SERVER_IP')
MQTT_SERVER_PORT = data.get('MQTT_SERVER_PORT')
MQTT_BASE_PATH   = data.get('MQTT_BASE_PATH')
MQTT_USERNAME    = data.get('MQTT_USERNAME')
MQTT_PASSWORD    = data.get('MQTT_PASSWORD')
STOVE_SERIAL     = data.get('STOVE_SERIAL')
STOVE_PIN        = data.get('STOVE_PIN')
MODE             = data.get('MODE')
STOVE_HEATLEVEL  = data.get('STOVE_HEATLEVEL')
STOVE_START_STOP = data.get('STOVE_START_STOP')

#-------------------------------------------------------------------------------
#MQTT stuff
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    dummy_block_statement = 0
    #print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #MQTT_BASE_PATH = "aduro_h2" + "/"
    #client.subscribe(MQTT_BASE_PATH)

# The callback when the client disconnects from server
async def on_disconnect(client, userdata,rc=0):
    #logging.debug("DisConnected result code "+str(rc))
    await client.loop_stop()

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    # more callbacks, etc
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Get Stove Discovery data
def get_discovery_data(aduro_cloud_backup_address = "apprelay20.stokercloud.dk"):
    from pyduro.actions import FUNCTIONS, STATUS_PARAMS, discover, get, set, raw
    import json

    result          = 0
    serial          = " "
    ip              = "no connection"
    device_type     = " "
    version         = " "
    build           = " "
    lang            = " "
    mqtt_json_data  = " "
    discovery_json  = " "

    try:
        response = discover.run()
        response = response.parse_payload()
    except:
        result = -1
        discovery_json = {"DISCOVERY": {"StoveSerial": serial, "StoveIP": ip, "NBE_Type": device_type, "StoveSWVersion": version, "StoveSWBuild": build, "StoveLanguage": lang}} 
        mqtt_json_data = json.dumps(discovery_json)
        return result, ip, serial, mqtt_json_data

    response = json.dumps(response)

    # JSON in ein Python-Dictionary umwandeln
    data = json.loads(response)

    # Variablen extrahieren
    serial      = data['Serial']
    ip          = data['IP']
    device_type = data['Type']
    version     = data['Ver']
    build       = data['Build']
    lang        = data['Lang']

    # check if IP is valid. fallback to Stove Cloud address if not valid    
    if "0.0.0.0" in ip:
        ip = aduro_cloud_backup_address

    if response:
        discovery_json = {"DISCOVERY": {"StoveSerial": serial, "StoveIP": ip, "NBE_Type": device_type, "StoveSWVersion": version, "StoveSWBuild": build, "StoveLanguage": lang}} 
        mqtt_json_data = json.dumps(discovery_json)
        result = 0
        #print(mqtt_json_data)
        return result, ip, serial, mqtt_json_data
    else:
        result = -1
        #print('no connection to stove')
        return result, ip, serial, mqtt_json_data
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Get Stove Consumption data
def get_consumption_data(ip, serial, pin):
    from pyduro.actions import FUNCTIONS, STATUS_PARAMS, discover, get, set, raw
    import json
    from datetime import date, timedelta

    try:
        response = raw.run(
            burner_address=str(ip),
            serial=str(serial),
            pin_code=str(pin),
            function_id=6,
            payload="total_days")

        data = response.payload.split(',')
        response = response.parse_payload()
    except:
        result = -1
        return result
    data[0] = data[0][11:(len(data[0]))] #remove total_days from string

    count = 0
    for i in data:
        #print(str(count+1) + ":" + str(data[count])) #count+1 for month calender date
        count = count + 1

    today = date.today().day #get current day from calender
    yesterday = date.today() - timedelta(1)
    yesterday = yesterday.day

    consumption_today = data[today-1] #get current day data
    consumption_yesterday = data[yesterday-1]

    # Get consumption data month
    response = raw.run(
        burner_address=str(ip),
        serial=str(serial),
        pin_code=str(pin),
        function_id=6,
        payload="total_months")

    data = response.payload.split(',')
    try:
        response = response.parse_payload()
    except:
        result = -1
        return result, mqtt_json_data
    data[0] = data[0][13:(len(data[0]))] #remove total_month from string

    count = 0
    for i in data:
        #print(str(count+1) + ":" + str(data[count])) #count+1 for month calender date
        count = count + 1

    month = date.today().month #get current month from calender

    consumption_month = data[month-1] #get current month data

    # Get consumption data year
    response = raw.run(
        burner_address=str(ip),
        serial=str(serial),
        pin_code=str(pin),
        function_id=6,
        payload="total_years")

    data = response.payload.split(',')
    try:
        response = response.parse_payload()
    except:
        result = -1
        return result, mqtt_json_data
    data[0] = data[0][12:(len(data[0]))] #remove total_years from string

    count = 0
    for i in data:
        #print(str(count) + ":" + str(data[count]))
        count = count + 1

    year = date.today().year #get current month from calender
    data_position_offset = year - (year-(len(data)-1)) #calculate data array position from current year. 2013 is data[0]...

    if response:
        consumption_json = {"CONSUMPTION": {"Day": consumption_today, "Yesterday": consumption_yesterday, "Month": consumption_month, "Year": data[data_position_offset]}} 
        mqtt_json_data = json.dumps(consumption_json)
        #print(mqtt_json_data)
        result = 0
        return result, mqtt_json_data
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Get Stove Status Data
def get_status(ip, serial, pin):
    from pyduro.actions import FUNCTIONS, STATUS_PARAMS, discover, get, set, raw
    import json

    result = 0 
    mqtt_json_data = " "

    try:
        response = raw.run(
            burner_address=str(ip),
            serial=str(serial),
            pin_code=str(pin),
            function_id=11,
            payload="*"
            )

        status = response.parse_payload().split(",")
        response = response.parse_payload()
    except:
        result = -1
        return result, mqtt_json_data

    i = 0
    for key in STATUS_PARAMS:
        STATUS_PARAMS[key] = status[i]
        i += 1

    if response:
        status_json = {"STATUS": STATUS_PARAMS}
        mqtt_json_data = json.dumps(status_json)
        #print(mqtt_json_data)
        result = 0
        return result, mqtt_json_data
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Get Stove Network Data
def get_network_data(ip, serial, pin):
    from pyduro.actions import FUNCTIONS, STATUS_PARAMS, discover, get, set, raw
    import json

    result = 0
    mqtt_json_data = " "

    try:
        response = raw.run(
            burner_address=str(ip),
            serial=str(serial),
            pin_code=str(pin),
            function_id=1,
            payload="wifi.router"
            )

        data = response.payload.split(',')
        response = response.parse_payload()
    except:
        result = -1
        return result, mqtt_json_data

    count = 0
    for i in data:
        #print(str(count) + ":" + str(data[count]))
        count = count + 1

    stove_ssid = data[0][7:(len(data[0]))]
    stove_ip = data[4]
    router_ip = data[5]
    stove_rssi = data[6]
    stove_mac = data[9]

    if response:
        network_json = {"NETWORK": {"RouterSSID": stove_ssid, "StoveIP": stove_ip, "RouterIP": router_ip, "StoveRSSI": stove_rssi, "StoveMAC": stove_mac}} 
        mqtt_json_data = json.dumps(network_json)
        #print(mqtt_json_data)
        result = 0
        return result, mqtt_json_data
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Get Stove Operating Data
def get_operating_data(ip, serial, pin):
    from pyduro.actions import FUNCTIONS, STATUS_PARAMS, discover, get, set, raw
    import json

    result = 0
    mqtt_json_data = " "

    response = raw.run(
        burner_address=str(ip),
        serial=str(serial),
        pin_code=str(pin),
        function_id=11,
        payload="001*"
        )
    #print("arduro 11")
    try:
        data = response.payload.split(',')
        response = response.parse_payload()
    except:
        result = -1
        return result, mqtt_json_data
    count = 0
    for i in data:
        #print(str(count) + ":" + str(data[count]))
        count = count + 1
    boiler_temp = data[0]
    boiler_ref = data[1]
    dhw_temp = data[4]
    state = data[6]
    substate = data[5]
    power_kw = data[31]
    power_pct = data[36]
    shaft_temp = data[35]
    smoke_temp = data[37]
    internet_uptime = data[38]
    milli_ampere = data[24]
    oxygen = data[26]
    router_ssid = data[68]
    date_stove = data[94][0:5]+"/"+str(20)+data[94][6:8]
    time_stove = data[94][9:(len(data[94]))]
    operating_time_auger = data[119]   #in seconds
    operating_time_ignition = data[120]#in seconds
    operating_time_stove = data[121]   #in seconds

    if response:
        operating_data_json = {"OPERATING": {"Power_kw": power_kw, "Power_pct": power_pct, "SmokeTemp": smoke_temp, "ShaftTemp": shaft_temp, "TimeStove": time_stove, "DateStove": date_stove, "State": state, "OperatingTimeAuger": operating_time_auger, "OperatingTimeStove": operating_time_stove, "OperatingTimeIgnition": operating_time_ignition}} 
        mqtt_json_data = json.dumps(operating_data_json)
        #print(mqtt_json_data)
        result = 0
        return result, mqtt_json_data
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Set Heatlevel
def set_heatlevel(ip, STOVE_SERIAL, STOVE_PIN, heatlevel):
    from pyduro.actions import FUNCTIONS, STATUS_PARAMS, discover, get, set, raw
    import json

    if heatlevel == 1:
        fixed_power = 10
    elif heatlevel == 2:
        fixed_power = 50
    elif heatlevel == 3:
        fixed_power = 100
    
    response = set.run( burner_address=str(ip),
                        serial=str(STOVE_SERIAL),
                        pin_code=str(STOVE_PIN),
                        path="regulation.fixed_power",
                        value=fixed_power
                        )
    data = response.parse_payload()
    #print(data)
    if data == "":
        result = 0
    else:
        result = -1
        return result
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Set to Force Anger Run
def set_force_auger(ip, STOVE_SERIAL, STOVE_PIN):
    from pyduro.actions import FUNCTIONS, STATUS_PARAMS, discover, get, set, raw
    import json

    response = set.run( burner_address=str(ip),
                        serial=str(STOVE_SERIAL),
                        pin_code=str(STOVE_PIN),
                        path="auger.forced_run",
                        value=1
                        )
    data = response.parse_payload()
    #print(data)
    if data == "":
        result = 0
    else:
        result = -1
        return result
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Set Stove Pellet Start/Stop
def set_start_stop(ip, STOVE_SERIAL, STOVE_PIN, start_stop):
    from pyduro.actions import FUNCTIONS, STATUS_PARAMS, discover, get, set, raw
    import json

    if start_stop == "start":
        set_value = "misc.start"
    elif start_stop == "stop":
        set_value = "misc.stop"
    
    response = set.run( burner_address=str(ip),
                        serial=str(STOVE_SERIAL),
                        pin_code=str(STOVE_PIN),
                        path=set_value,
                        value=1
                        )
    data = response.parse_payload()
    #print(data)
    if data == "":
        result = 0
    else:
        result = -1
        return result
#--------------------------------------------------------------------------------

#--------------------------------[MAIN]-----------------------------------------
#logger.info(f"starting Pyduro script!")

#init Mqtt stuff if script shall send mqtt data
if MQTT_SERVER_IP != None:
    client = mqtt.Client()
    client.on_connect == on_connect
    client.on_message = on_message
    client.username_pw_set(username=MQTT_USERNAME,password=MQTT_PASSWORD)
    client.connect(MQTT_SERVER_IP, MQTT_SERVER_PORT, 60)
    client.subscribe(MQTT_BASE_PATH)
    client.loop_start()
#-------------------------------------------------------------------------------

# get previous discovered stove IP from Home Assistant
ip = hass.states.get('sensor.aduro_h2_stove_ip').state
#logger.info(f"IP from HA:{ ip}")

# check if IP is valid. fallback to Stove Cloud address if not valid
aduro_cloud_backup_address = "apprelay20.stokercloud.dk"

# workaround if stove lost router ipv4 -> switch to cloud server address 
if "0.0.0.0" in ip or ip == "unknown" or ip == "no connection" or ip == aduro_cloud_backup_address:
    try:
        result, ip, serial, mqtt_json_discover_data = get_discovery_data()
        if "0.0.0.0" in ip:
            ip = aduro_cloud_backup_address

        discovery_json = json.loads(mqtt_json_discover_data)
        discovery_json['DISCOVERY']['StoveIP'] = ip
        discovery_json['DISCOVERY']['StoveSerial'] = serial
        mqtt_json_discover_data = json.dumps(discovery_json)

        if MQTT_SERVER_IP != None:
            client.publish(MQTT_BASE_PATH + "discovery", str(mqtt_json_discover_data))
            time.sleep(0.2)
    except:
        #logger.info(f"Discovery Exeption!")
        if MQTT_SERVER_IP != None:
            client.disconnect()
        exit()
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Get Stove Discovery data    
if MODE == "discover" or MODE == "all":
    try:
        result, ip, serial, mqtt_json_discover_data = get_discovery_data()
        client.publish(MQTT_BASE_PATH + "discovery", str(mqtt_json_discover_data))
        time.sleep(0.2)
    except:
        #retries 3 times
        for x in range(0, 3):
            #print("Discovery retry: %2d" %x)
            time.sleep(1)
            result, ip, serial, mqtt_json_discover_data = get_discovery_data()
            if result != -1:
                client.publish(MQTT_BASE_PATH + "discovery", str(mqtt_json_discover_data))
                time.sleep(0.2)
                break
        client.disconnect()
        exit()
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Get Stove network data
if MODE == "network" or MODE == "all":
    try:
        result, mqtt_json_network_data = get_network_data(ip, STOVE_SERIAL, STOVE_PIN)
        client.publish(MQTT_BASE_PATH + "network", str(mqtt_json_network_data))
        time.sleep(0.2)
    except:
        #retries 3 times
        for x in range(0, 3):
            time.sleep(1)
            result, ip, serial, mqtt_json_discover_data = get_discovery_data()
            result, mqtt_json_network_data = get_network_data(ip, STOVE_SERIAL, STOVE_PIN)
            if result != -1:
                client.publish(MQTT_BASE_PATH + "network", str(mqtt_json_network_data))
                time.sleep(0.2)
                break
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Get consumption data today and yesterday
if MODE == "consumption" or MODE == "all":
    try:
        result, mqtt_json_consumption_data = get_consumption_data(ip,STOVE_SERIAL,STOVE_PIN)                
        client.publish(MQTT_BASE_PATH + "consumption_data", str(mqtt_json_consumption_data))
        time.sleep(0.2)
    except:
        #retries 3 times
        for x in range(0, 3):
            time.sleep(1)
            result, ip, serial, mqtt_json_discover_data = get_discovery_data()
            result, mqtt_json_consumption_data = get_consumption_data(ip,STOVE_SERIAL,STOVE_PIN)                
            if result != -1:
                client.publish(MQTT_BASE_PATH + "consumption_data", str(mqtt_json_consumption_data))
                time.sleep(0.2)
                break
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Get Status
if MODE == "status" or MODE == "all":
    try:
        result, mqtt_json_status_data = get_status(ip, STOVE_SERIAL, STOVE_PIN)
        client.publish(MQTT_BASE_PATH + "status", str(mqtt_json_status_data))
        time.sleep(0.2)
    except:
        #retries 3 times
        for x in range(0, 3):
            time.sleep(1)
            result, ip, serial, mqtt_json_discover_data = get_discovery_data()
            result, mqtt_json_status_data = get_status(ip, STOVE_SERIAL, STOVE_PIN)
            if result != -1:
                client.publish(MQTT_BASE_PATH + "status", str(mqtt_json_status_data))
                time.sleep(0.2)
                break
#-------------------------------------------------------------------------------
if MODE == "set_heatlevel":
    try:
        result = set_heatlevel(ip, serial, STOVE_PIN, STOVE_HEATLEVEL)
    except:
        #retries 3 times
        for x in range(0, 3):
            time.sleep(1)
            result, ip, serial, mqtt_json_discover_data = get_discovery_data()
            result = set_heatlevel(ip, serial, STOVE_PIN, STOVE_HEATLEVEL)
            if result != -1:
                break
#---------------------------------------------------------------------------------
if MODE == "set_force_auger":
    try:
        result = set_force_auger(ip, STOVE_SERIAL, STOVE_PIN)
    except:
        #retries 3 times
        for x in range(0, 3):
            time.sleep(1)
            result, ip, serial, mqtt_json_discover_data = get_discovery_data()
            result = set_force_auger(ip, STOVE_SERIAL, STOVE_PIN)
            if result != -1:
                break
#---------------------------------------------------------------------------------
if MODE == "set_start_stop":
    try:
        result = set_start_stop(ip, serial, STOVE_PIN, STOVE_START_STOP)
    except:
        #retries 3 times
        for x in range(0, 3):
            time.sleep(1)
            result, ip, serial, mqtt_json_discover_data = get_discovery_data()
            result = set_start_stop(ip, serial, STOVE_PIN, STOVE_START_STOP)
            if result != -1:
                break
#---------------------------------------------------------------------------------
if MQTT_SERVER_IP != None:
    client.disconnect()
