#!/usr/bin/python3

import paho.mqtt.client as mqtt
import time

ID = 1
GAME_SERVER = list()
PLAYERS = list()
#def move()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("tictactoe/request/delegation")
    client.subscribe("tictactoe/move/+")
    client.subscribe("tictactoe/connected")

def on_message(client, userdata, msg):
    global ID
    msg.payload = msg.payload.decode("utf-8")
    if msg.topic == "tictactoe/move/0":
        print("Placing an X")
    elif msg.topic == "tictactoe/move/1":
        print("Placing an O")
    elif msg.topic == "tictactoe/request/delegation":
        client.publish("tictactoe/delegation", str(ID))
        print("request/delegation" + " " +  str(ID))
        PLAYERS.append(int(ID))
        time.sleep(2)
        print("tictactoe/player/"+str(ID)+"/game", 1)
        client.publish("tictactoe/player/"+str(ID)+"/game", 1)
        ID += 1
       

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("93.166.88.200", 1883, 60)
client.loop_forever()