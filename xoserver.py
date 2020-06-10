#!/usr/bin/python3

import paho.mqtt.client as mqtt

ID = 1
#def move()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("tictactoe/request/delegation")
    client.subscribe("tictactoe/move/+")

def on_message(client, userdata, msg):
    global ID
    msg.payload = msg.payload.decode("utf-8")
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == "tictactoe/move/0":
        print("Placing an X")
    elif msg.topic == "tictactoe/move/1":
        print("Placing an O")
    elif msg.topic == "tictactoe/request/delegation":
        print("request/delegation" + " " +  str(ID))
        client.publish("tictactoe/delegation", str(ID))
        ID += 1

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("93.166.88.200", 1883, 60)
client.loop_forever()