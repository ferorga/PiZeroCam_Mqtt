import subprocess
import paho.mqtt.client as mqtt
import time
import psutil

mqtt_username = "mqtt-user"
mqtt_password = "HAmqtt"
mqtt_host = "192.168.20.100"
mqtt_port = 1883
status_topic = "homeassistant/piz/status"
status_payload = {"state": "online"}
rtsp_topic = "homeassistant/button/piz/rtsp/set"
rtsp_status_topic = "homeassistant/button/piz/rtsp"

def is_rtsp_server_running():
    try:
        subprocess.run(["systemctl", "is-active", "--quiet", "raspivid_service.service"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def start_subprocess():
    print(f"Starting service")
    subprocess.call(["sudo systemctl start raspivid_service.service"], shell=True)
    time.sleep(2)

def stop_subprocess():
    print(f"Stop service")
    subprocess.call(["sudo systemctl stop raspivid_service.service"], shell=True)
    time.sleep(2)

def on_message(client, userdata, message):
    print(f"Message received:", str(message.payload.decode("utf-8")))
    if message.payload.decode("utf-8") == "off":
        stop_rtsp_server()
    elif message.payload.decode("utf-8") == "on":
        start_rtsp_server()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code " + str(rc))
    print(f"Subscribing to topic", rtsp_topic)
    client.subscribe(rtsp_topic)
    if is_rtsp_server_running():
        client.publish(topic=rtsp_status_topic, payload="on", qos=0, retain=True)
    else:
        client.publish(topic=rtsp_status_topic, payload="off", qos=0, retain=True)

def start_rtsp_server():
    print(f"Starting raspivid")

    start_subprocess()

    if is_rtsp_server_running():
        client.publish(topic=rtsp_status_topic, payload="on", qos=0, retain=True)
        print(f"Started successfully")
    else:
        print(f"Error starting video sender")
    

def stop_rtsp_server():
    print(f"Stopping raspivid")
    stop_subprocess()
    client.publish(topic=rtsp_status_topic, payload="off", qos=0, retain=True)


print(f"Creating new instance")
client = mqtt.Client("PiZeroClient")
client.username_pw_set(mqtt_username, mqtt_password)
print(f"Connecting to broker")
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_host, mqtt_port)
client.loop_start()

while True:
    print(f"Sending status")
    client.publish(topic=status_topic, payload="online", qos=0, retain=False)
    time.sleep(5)
