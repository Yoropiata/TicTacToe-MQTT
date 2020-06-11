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
    #print(msg.topic+" "+str(msg.payload))
    if msg.topic == "tictactoe/move/0":
        print("Placing an X")
    elif msg.topic == "tictactoe/move/1":
        print("Placing an O")
    elif msg.topic == "tictactoe/request/delegation":
        print("request/delegation" + " " +  str(ID))
        client.publish("tictactoe/delegation", str(ID))
        PLAYERS.append(int(ID))
        client.publish("tictactoe/player/"+str(ID)+"/game", 1)#str(ID)
        ID += 1
    elif msg.topic == "tictactoe/connected":
       PLAYERS.append(int(msg.payload))
       

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("10.0.0.14", 1883, 60)
client.loop_forever()
#client.loop_start()

#while True:
#  for player in PLAYERS:
#    client.publish("tictactoe/player/"+str(player)+"/connected", str(player))
#    PLAYERS.remove(player)
  
#  time.sleep(1)