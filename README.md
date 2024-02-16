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

Example for get all status informations
```python
pyduro_mqtt_all:
  sequence:
    - service: python_script.exec
      data:
        file: python_scripts/pyduro_mqtt.py
        STOVE_SERIAL: 12345
        STOVE_PIN: 12345678
        MQTT_SERVER_IP: 192.168.0.2
        MQTT_SERVER_PORT: 1883
        MQTT_USERNAME: max
        MQTT_PASSWORD: powers
        MQTT_BASE_PATH: "aduro_h2/"
        MODE: all
        cache: false
```
MODE Options:
```
all (get all data "discover, network, consumption")
discover (get discovery data only)
network (get network data only)
consumption (get consumption data only)
set_start_stop (start or stop the stove. HASS parameter STOVE_START_STOP: <start|stop> must be provided to data:)
set_force_auger (force auger for some seconds for manual pellet feeding)
set_heatlevel (set heatlevel of stove HASS parameter STOVE_HEATLEVEL: <1|2|3> must be provided to data:)
```

-> check out script.yaml for more details ...
```python
pyduro_mqtt_all:
  sequence:
    - service: python_script.exec
      data:
        file: python_scripts/pyduro_mqtt.py
        STOVE_SERIAL: 12345
        STOVE_PIN: 123456789
        MQTT_SERVER_IP: 192.168.0.2
        MQTT_SERVER_PORT: 1883
        MQTT_USERNAME: max
        MQTT_PASSWORD: powers
        MQTT_BASE_PATH: "aduro_h2/"
        MODE: all
        cache: false
      #response_variable: result

pyduro_mqtt_discover:
  sequence:
    - service: python_script.exec
      data:
        file: python_scripts/pyduro_mqtt.py
        STOVE_SERIAL: 12345
        STOVE_PIN: 123456789
        MQTT_SERVER_IP: 192.168.0.2
        MQTT_SERVER_PORT: 1883
        MQTT_USERNAME: max
        MQTT_PASSWORD: powers
        MQTT_BASE_PATH: "aduro_h2/"
        MODE: discover
        cache: false

pyduro_mqtt_network:
  sequence:
    - service: python_script.exec
      data:
        file: python_scripts/pyduro_mqtt.py
        STOVE_SERIAL: 12345
        STOVE_PIN: 123456789
        MQTT_SERVER_IP: 192.168.0.2
        MQTT_SERVER_PORT: 1883
        MQTT_USERNAME: max
        MQTT_PASSWORD: powers
        MQTT_BASE_PATH: "aduro_h2/"
        MODE: network
        cache: false

pyduro_mqtt_consumption:
  sequence:
    - service: python_script.exec
      data:
        file: python_scripts/pyduro_mqtt.py
        STOVE_SERIAL: 12345
        STOVE_PIN: 123456789
        MQTT_SERVER_IP: 192.168.0.2
        MQTT_SERVER_PORT: 1883
        MQTT_USERNAME: max
        MQTT_PASSWORD: powers
        MQTT_BASE_PATH: "aduro_h2/"
        MODE: consumption
        cache: false

pyduro_mqtt_status:
  sequence:
    - service: python_script.exec
      data:
        file: python_scripts/pyduro_mqtt.py
        STOVE_SERIAL: 12345
        STOVE_PIN: 123456789
        MQTT_SERVER_IP: 192.168.0.2
        MQTT_SERVER_PORT: 1883
        MQTT_USERNAME: max
        MQTT_PASSWORD: powers
        MQTT_BASE_PATH: "aduro_h2/"
        MODE: status
        cache: false

pyduro_start:
  sequence:
    - service: python_script.exec
      data:
        file: python_scripts/pyduro_mqtt.py
        STOVE_SERIAL: 12345
        STOVE_PIN: 123456789
        MODE: set_start_stop
        STOVE_START_STOP: start
        cache: false

pyduro_stop:
  sequence:
    - service: python_script.exec
      data:
        file: python_scripts/pyduro_mqtt.py
        STOVE_SERIAL: 12345
        STOVE_PIN: 123456789
        MODE: set_start_stop
        STOVE_START_STOP: stop
        cache: false

pyduro_force_auger:
  sequence:
    - service: python_script.exec
      data:
        file: python_scripts/pyduro_mqtt.py
        STOVE_SERIAL: 12345
        STOVE_PIN: 123456789
        MODE: set_force_auger
        cache: false

pyduro_heatlevel_1:
  sequence:
    - service: python_script.exec
      data:
        file: python_scripts/pyduro_mqtt.py
        STOVE_SERIAL: 12345
        STOVE_PIN: 123456789
        MODE: set_heatlevel
        STOVE_HEATLEVEL: 1
        cache: false

pyduro_heatlevel_2:
  sequence:
    - service: python_script.exec
      data:
        file: python_scripts/pyduro_mqtt.py
        STOVE_SERIAL: 12345
        STOVE_PIN: 123456789
        MODE: set_heatlevel
        STOVE_HEATLEVEL: 2
        cache: false

pyduro_heatlevel_3:
  sequence:
    - service: python_script.exec
      data:
        file: python_scripts/pyduro_mqtt.py
        STOVE_SERIAL: 12345
        STOVE_PIN: 123456789
        MODE: set_heatlevel
        STOVE_HEATLEVEL: 3
        cache: false
```

You need to add mqtt entities, that the mqtt data is used by homeassistant.
-> example... put the entities in your configuration.yaml or your dedicated mqtt yaml file 

```python
sensor:
  - name: "Aduro H2 Smoke Temperature"
      unique_id: sensor.aduro_smoketemperature
      state_topic: "aduro_h2/status"
      #state_class: measurement
      value_template: "{{(value_json['STATUS']['smoke_temp']) | float | round(1)}}"
      unit_of_measurement: "°C"
      device_class: temperature
  
    - name: "Aduro H2 Shaft Temperature"
      unique_id: sensor.aduro_shafttemperature
      state_topic: "aduro_h2/status"
      #state_class: measurement
      value_template: "{{(value_json['STATUS']['shaft_temp']) | float | round(1)}}"
      unit_of_measurement: "°C"
      device_class: temperature
  
    - name: "Aduro H2 Power kW"
      unique_id: sensor.aduro_power_kw
      state_topic: "aduro_h2/status"
      state_class: measurement
      value_template: "{{(value_json['STATUS']['power_kw']|float) | round(1)}}"
      unit_of_measurement: "kW"
      #device_class: energy
  
    - name: "Aduro H2 Power W"
      unique_id: sensor.aduro_power_w
      state_topic: "aduro_h2/status"
      state_class: measurement
      value_template: "{{(value_json['STATUS']['power_kw']|float * 1000) | round(1)}}"
      unit_of_measurement: "W"
      #device_class: energy
  
    - name: "Aduro H2 State"
      unique_id: sensor.aduro_state
      state_topic: "aduro_h2/status"
      value_template: "{{(value_json['STATUS']['state']|float) | round(0)}}"
  
    - name: "Aduro H2 Substate"
      unique_id: sensor.aduro_substate
      state_topic: "aduro_h2/status"
      value_template: "{{(value_json['STATUS']['substate']|float) | round(0)}}"
  
    - name: "Aduro H2 Oxygen"
      unique_id: sensor.aduro_oxygen
      state_topic: "aduro_h2/status"
      value_template: "{{(value_json['STATUS']['oxygen']|float) | round(1)}}"
      unit_of_measurement: "ppm"
  
    - name: "Aduro H2 Consumption Day"
      unique_id: sensor.aduro_consumption_day
      state_topic: "aduro_h2/consumption_data"
      state_class: measurement
      unit_of_measurement: "kg"
      value_template: "{{(value_json.CONSUMPTION.Day|float) | float | round(3)}}"
      #device_class: energy
  
    - name: "Aduro H2 Consumption Yesterday"
      unique_id: sensor.aduro_consumption_yesterday
      state_topic: "aduro_h2/consumption_data"
      state_class: measurement
      unit_of_measurement: "kg"
      value_template: "{{(value_json.CONSUMPTION.Yesterday|float) | round(3)}}"
      #device_class: energy
  
    - name: "Aduro H2 Consumption Month"
      unique_id: sensor.aduro_consumption_month
      state_topic: "aduro_h2/consumption_data"
      state_class: measurement
      unit_of_measurement: "kg"
      value_template: "{{(value_json.CONSUMPTION.Month|float) |float | round(3)}}"
      #device_class: energy
  
    - name: "Aduro H2 Consumption Year"
      unique_id: sensor.aduro_consumption_year
      state_topic: "aduro_h2/consumption_data"
      state_class: measurement
      unit_of_measurement: "kg"
      value_template: "{{(value_json.CONSUMPTION.Year|float) |float | round(3)}}"
      #device_class: energy
  
    - name: "Aduro H2 Stove Serial"
      unique_id: sensor.aduro_stove_serial
      state_topic: "aduro_h2/discovery"
      value_template: "{{(value_json.DISCOVERY.StoveSerial)}}"
  
    - name: "Aduro H2 Stove IP"
      unique_id: sensor.aduro_stove_ip
      state_topic: "aduro_h2/discovery"
      value_template: "{{(value_json.DISCOVERY.StoveIP)}}"
  
    - name: "Aduro H2 Stove Heatlevel"
      unique_id: sensor.aduro_stove_heatlevel
      state_topic: "aduro_h2/status"
      #value_template: "{{(value_json['STATUS']['regulation.fixed_power']|float)|float | round(0)}}"
      value_template: >-
        {%   if (value_json['STATUS']['regulation.fixed_power']|float)|float | round(0)   == 10 %}
        1
        {% elif (value_json['STATUS']['regulation.fixed_power']|float)|float | round(0) == 50 %}
        2
        {% elif (value_json['STATUS']['regulation.fixed_power']|float)|float | round(0) == 100 %}
        3
        {% endif %}
#------------------------------------------------------------------------------

```


