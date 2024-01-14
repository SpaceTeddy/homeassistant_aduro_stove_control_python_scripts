# homeassistant_aduro_stove_control_python_scripts
This script can be used to control your Aduro Hybrid stove via Homeassistant

It requires PythonScriptsPro (https://github.com/AlexxIT/PythonScriptsPro) for HA and pyduro (https://github.com/clementprevot/pyduro) as standard python library to get connection to the stove. In addition, paho-mqtt (https://github.com/eclipse/paho.mqtt.python) library is required for python mqtt connectifity. 

After all files are saved into HA directories and HA restarted, you has access to HA `Python Scripts Pro: exec` service call.
As an example you can use following Service data parameter to read out the stove status data:


file: python_scripts/pyduro_mqtt.py <br />
STOVE_SERIAL: your stove serial <br />
STOVE_PIN: your stove pw <br />
MQTT_SERVER_IP: your mqtt broker IP <br />
MQTT_SERVER_PORT: 1883 <br />
MQTT_USERNAME: client username <br />
MQTT_PASSWORD: client PW <br />
MQTT_BASE_PATH: "aduro_h2/" <br />
MODE: status <br />
cache: false <br />

