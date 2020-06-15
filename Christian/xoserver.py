#!/usr/bin/python3

import paho.mqtt.client as mqtt
import time

ID = 1
GAME_SERVER = list()
PLAYERS = list()
board = [list('   ') for _ in range(3)]
x_pos = 0
y_pos = 0

def check_victory(board, y, x):
    #check if previous move caused a win on horizontal line
    if board[0][x] == board[1][x] == board [2][x]:
        return True

    #check if previous move caused a win on vertical line
    if board[y][0] == board[y][1] == board [y][2]:
        return True

    #check if previous move was on the main diagonal and caused a win
    if x == y and board[0][0] == board[1][1] == board [2][2]:
        return True

    #check if previous move was on the secondary diagonal and caused a win
    if x + y == 2 and board[0][2] == board[1][1] == board [2][0]:
        return True

    return False     

def check(board, y, x, ch):
    if check_victory(board, int(y_pos), int(x_pos)):
                client.publish("tictactoe/server/", "Win: "+ str(ch))

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("tictactoe/request/#")
    client.subscribe("tictactoe/move/+")
    client.subscribe("tictactoe/connected")
    client.subscribe("tictactoe/server/+/move/#")

def on_message(client, userdata, msg):
    global ID, board, x_pos, y_pos
    msg.payload = msg.payload.decode("utf-8")
    if msg.topic == "tictactoe/move/0":
        print("Placing an X")
    elif msg.topic == "tictactoe/move/1":
        print("Placing an O")
    elif msg.topic == "tictactoe/request/delegation":
        client.publish("tictactoe/delegation", str(ID))
        print("request/delegation" + " " +  str(ID))
        PLAYERS.append(int(ID))
        ID += 1
    elif msg.topic == "tictactoe/request/server":
        print("tictactoe/player/"+str(msg.payload)+"/game: 1")
        client.publish("tictactoe/player/"+str(msg.payload)+"/game", 1)
    elif msg.topic == "tictactoe/server/1/move/X":
        pos = int(msg.payload)
        x = pos % 3
        y = (pos - x)/3
        x_pos = int(x)
        y_pos = int(y)
        board[y_pos][x_pos] = 'X'
        if check_victory(board, y_pos, x_pos):
                client.publish("tictactoe/server/1/victory", "X") 
    elif msg.topic == "tictactoe/server/1/move/O":
        pos = int(msg.payload)
        x = pos % 3
        y = (pos - x)/3
        x_pos = int(x)
        y_pos = int(y)
        board[int(y_pos)][int(x_pos)] = 'O'
        if check_victory(board, y_pos, x_pos):
                client.publish("tictactoe/server/1/victory", "O")  

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("93.166.88.200", 1883, 60)
client.loop_forever()