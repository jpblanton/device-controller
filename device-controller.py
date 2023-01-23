import argparse
import atexit

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO


def cleanup(client):
    GPIO.cleanup()
    client.loop_stop()

def on_message(client, userdata, message):
    payload = message.payload
    device_name = '_'.join(message.topic.split('/')[:2])
    pin = userdata['config'][device_name]['gpio_pin']
    pub_topic = userdata['config'][device_name]['pub_topic']
    err_topic = userdata['config'][device_name]['err_topic']
    if payload == b'True':
        GPIO.output(pin, GPIO.LOW)
        client.publish(pub_topic, True)
    elif payload == b'False':
        GPIO.output(pin, GPIO.HIGH)
        client.publish(pub_topic, False)
    else:
        client.publish(err_topic, f"Invalid value in payload: {payload}")


def mqtt_connect(topics: list[str], host: str, userdata: dict):
    client = mqtt.Client(userdata=userdata)
    client.connect(host, 1883)
    for topic in topics:
        client.subscribe(topic)
    return client


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, required=True, help='Hostname or IP of the MQTT broker')
    parser.add_argument('--config', type=str, default='device-config.toml')
    args = parser.parse_args()

    with open(args.config, 'rb') as f:
        config = tomllib.load(f)
    
    GPIO.setmode(GPIO.BCM)
    sub_topics = [config[dev]['sub_topic'] for dev in config]
    for device in config:
        GPIO.setup(config[device]['gpio_pin'], GPIO.OUT)

    client_userdata = {'config': config}
    client = mqtt_connect(sub_topics, args.host, client_userdata)
    client.on_message = on_message
    atexit.register(cleanup, client)
    client.loop_forever()
