# #!/usr/bin/python3

import paho.mqtt.client as mqtt
import time
import re
from game_server_type import GameServer


ID = 1
GAME_SERVERS = list()
PLAYERS = list()
#def move()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("tictactoe/request/+")
    client.subscribe("tictactoe/server/+/move/+")
    client.subscribe("tictactoe/connected")

def on_message(client, userdata, msg):
    global ID, GAME_SERVERS, PLAYERS
    msg.payload = msg.payload.decode("utf-8")
    print(msg.topic + " - " + msg.payload)
    if msg.topic == "tictactoe/request/playerid":
        user_id = ID
        ID += 1
        print("request/delegation" + " " +  str(user_id))
        PLAYERS.append(int(user_id))

        if len(GAME_SERVERS) > 0:
            #Check for game servers that need a player2.
            for i in range(len(GAME_SERVERS)):
                game_server = GAME_SERVERS[i]
                if game_server.player2 is None:
                    game_server.player2 = user_id
            #Create a new game server
            GAME_SERVERS.append(GameServer(user_id))
        else:
            #Create a new game server
            GAME_SERVERS.append(GameServer(user_id))
        client.publish("tictactoe/delegation", str(user_id))
    elif msg.topic == "tictactoe/request/gameserver":
        user_id = msg.payload
        for i in range(len(GAME_SERVERS)):
            game_server = GAME_SERVERS[i]
            if int(game_server.player1) == int(user_id) or int(game_server.player2) == int(user_id):
                client.publish("tictactoe/delegation/" + user_id, str(i))
                print("tictactoe/delegation/" + user_id + ", " + str(i))
                break

    elif re.search("tictactoe/server/.+/move/.+", msg.topic):
        user_id = int(msg.topic.split('/')[4])
        game_server_id = int(msg.topic.split('/')[2])
        game_server = GAME_SERVERS[game_server_id]
        pos = int(msg.payload)
        x = pos % 3
        y = (pos - x)/3
        x_pos = int(x)
        y_pos = int(y)
        game_server.board[y_pos][x_pos] = 'X' if user_id % 2 == 1 else 'O'
        user_won = game_server.check_victory(y_pos, x_pos)

        if user_won:
            print("VICTORY BY: " + str(user_id))
            client.publish("tictactoe/server/" + str(game_server_id) + "/victory", user_id)


    # elif msg.topic == "tictactoe/connected":
    #    PLAYERS.append(int(msg.payload))
       

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("93.166.88.200", 1883, 60)
client.loop_forever()