#!/usr/bin/python3

import paho.mqtt.client as mqtt
import time
from game_server_type import GameServer

ID = 1
GAME_SERVERS = list()
PLAYERS = list()
#def move()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("tictactoe/request/delegation")
    client.subscribe("tictactoe/move/+")
    client.subscribe("tictactoe/connected")

def on_message(client, userdata, msg):
    global ID, GAME_SERVERS
    msg.payload = msg.payload.decode("utf-8")
    if msg.topic == "tictactoe/request/playerid":
        client.publish("tictactoe/delegation", str(ID))
        PLAYERS.append(int(ID))

        if len(GAME_SERVERS > 0):
            #Check for game servers that need a player2.
            for i in range(len(GAME_SERVERS)):
                game_server = GAME_SERVERS[i]
                if game_server.player2 == 0:
                    game_server.player2 = ID
                    break
            #Create a new game server
            GAME_SERVERS.append(GameServer(ID))
        else:
            #Create a new game server
            GAME_SERVERS.append(GameServer(ID))
        ID += 1
    elif msg.topic == "tictactoe/request/gameserver":
        
        client.publish("tictactoe/delegation/game", str(ID))
        PLAYERS.append(int(ID))
        client.publish("tictactoe/player/"+str(ID)+"/game", 1)#str(ID)
    # elif msg.topic == "tictactoe/connected":
    #    PLAYERS.append(int(msg.payload))
       

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("93.166.88.200", 1883, 60)
client.loop_forever()
#client.loop_start()

#while True:
#  for player in PLAYERS:
#    client.publish("tictactoe/player/"+str(player)+"/connected", str(player))
#    PLAYERS.remove(player)
  
#  time.sleep(1)