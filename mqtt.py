#----------------------------------------------------------------------------------------------------------------
#   Class for MQTT connection to control the light
#
#   Author: Lutz Hager 
#   Date: 23.05.23
#
#----------------------------------------------------------------------------------------------------------------
import paho.mqtt.client as mqtt
import logging
logging.basicConfig(filename='app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')


class MQTT_CONNECTION:
    # MQTT broker configuration
    broker = "10.50.12.62"
    port = 1883
    topic = "DMX1"

    def __init__(self):
        try:
            # Create an MQTT client instance
            mqttClient = mqtt.Client()

            # Set up the callback functions
            mqttClient.on_connect = self.on_connect
            # mqttClient.on_message = on_message

            # Connect to the MQTT broker
            # client.username_pw_set(username="",password="password")
            mqttClient.connect(self.broker, self.port)

            # Start the MQTT client loop
            mqttClient.loop_start()

        except:
            logging.error("failed to connect to mqtt broker")


    # Callback function for when a connection is established
    def on_connect(self):
        logging.info("connected to mqqt broker")
        # Subscribe to the topic
        self.mqttClient.subscribe(self.topic)


    def publishMessage(self, topic, message):
        try:
            self.mqttClient.publish(topic, message)
        except:
            logging.error("failed to publish mqtt message")