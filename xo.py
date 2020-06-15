#!/usr/bin/python3

import curses
from curses import wrapper
import time
import paho.mqtt.client as mqtt

#Player characters
P1_CH = 'X'
P2_CH = 'O'
PLAYER_CH = ''
OPPONENT_CH = ''
#Move field
X_MOVE = 4
Y_MOVE = 2
#Board location
X_OFFSET = 1
Y_OFFSET = 4

RESPONS = False
X_RESPONS = 1
Y_RESPONS = 1
MOVE = 0
IGNORE = 0

GAME_ID = 0
MY_PLAYER_ID = 0
current_player_id = 1
player_id = 0

def on_connect(client, userdata, flags, rc):
    client.subscribe("tictactoe/delegation")
    client.publish("tictactoe/request/playerid","join")

def on_message(client, userdata, msg):
    global MY_PLAYER_ID, GAME_ID, RESPONS, X_RESPONS, Y_RESPONS, MOVE, IGNORE
    msg.payload = msg.payload.decode("utf-8")
    #Give player ID and subscribe to player
    if msg.topic == "tictactoe/delegation":
        if MY_PLAYER_ID == 0:
            MY_PLAYER_ID = int(msg.payload)
            current_player_id = MY_PLAYER_ID
            client.subscribe("tictactoe/player/"+str(MY_PLAYER_ID)+"/#")
            client.subscribe("tictactoe/player/"+str(MY_PLAYER_ID))
            client.subscribe("tictactoe/delegation/" + str(MY_PLAYER_ID))
            client.publish("tictactoe/request/gameserver", str(MY_PLAYER_ID))

    #Get game lobby
    elif msg.topic == "tictactoe/delegation/" + str(MY_PLAYER_ID):
        if GAME_ID == 0:
            GAME_ID == int(msg.payload)
    
    elif msg.topic == "tictactoe/server/"+str(GAME_ID)+"/victory":
        print(msg.payload)
        
    #Get game server
    elif msg.topic == "tictactoe/player/"+str(MY_PLAYER_ID)+"/game":
        GAME_ID = int(msg.payload)
        client.subscribe("tictactoe/server/"+str(GAME_ID)+"/#")
        client.publish("tictactoe/info", "game id : "+ str(GAME_ID))
        
    #Action
    elif msg.topic == "tictactoe/server/"+str(GAME_ID)+"/move/"+str(MY_PLAYER_ID):
        IGNORE = int(msg.payload)
    elif msg.topic == "tictactoe/server/"+str(GAME_ID)+"/move":
        client.publish("tictactoe/info", "info: "+ str(msg.payload))
        MOVE = int(msg.payload)
        x = MOVE % 3
        y = (MOVE - x)/3
        X_RESPONS = x
        Y_RESPONS = y
        RESPONS = True
    elif msg.topic == "tictactoe/victory":
        print(msg.payload)


#Draw Board
def draw_board(stdscr):
    stdscr.addstr(0, 0, 'Tic Tac Toe')
    stdscr.hline(1, 0, '-', 50)
    stdscr.addstr(2, 0, 'Use WASD or arrows to move,  [SPACE] Draw player char,  [Q] Quit')
    stdscr.addstr(Y_OFFSET    , X_OFFSET, '  |   |  ')
    stdscr.addstr(Y_OFFSET + 1, X_OFFSET, '--+---+--')
    stdscr.addstr(Y_OFFSET + 2, X_OFFSET, '  |   |  ')
    stdscr.addstr(Y_OFFSET + 3, X_OFFSET, '--+---+--')
    stdscr.addstr(Y_OFFSET + 4, X_OFFSET, '  |   |  ')

#Draw player char
def draw(y, x, stdscr, player_ids):
    stdscr.addch(y, x, player_ids)#P2_CH if player_ids else P1_CH)

#stdscr - default window
def main(stdscr):
    global RESPONS, current_player_id, MY_PLAYER_ID, PLAYER_CH, OPPONENT_CH, current_player_id, player_id
    # Clear screen
    # stdscr.clear()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("93.166.88.200", 1883, 60)
    client.loop_start()


    PLAYER_CH = P2_CH if MY_PLAYER_ID %2 else P1_CH
    OPPONENT_CH = P1_CH if MY_PLAYER_ID %2 else P2_CH
    
    draw_board(stdscr)

    x_pos = 1
    y_pos = 1
    board = [list('   ') for _ in range(3)]

          
    while True:
        stdscr.move(Y_OFFSET + y_pos * Y_MOVE, X_OFFSET + x_pos * X_MOVE)
        
        if current_player_id != MY_PLAYER_ID and RESPONS == True:
            x = int(X_RESPONS) * X_MOVE + X_OFFSET
            y = int(Y_RESPONS) * Y_MOVE + Y_OFFSET
            draw(y, x, stdscr, OPPONENT_CH)
            board[y_pos][x_pos] = OPPONENT_CH
            current_player_id = MY_PLAYER_ID
            stdscr.addstr(7, 0, 'Placed OPPONENT element')
            stdscr.refresh()
            RESPONS = False

        #Move options
        key = stdscr.getch()
        if key == curses.KEY_UP or key == ord('w'):
            y_pos = max(0, y_pos - 1)
        elif key == curses.KEY_DOWN or key == ord('s'):
            y_pos = min(2, y_pos + 1)
        elif key == curses.KEY_LEFT or key == ord('a'):
            x_pos = max(0, x_pos - 1)
        elif key == curses.KEY_RIGHT or key == ord('d'):
            x_pos = min(2, x_pos + 1)
        elif key == ord('q') or key == ord('Q'):
            break
        elif key == ord(' ') and current_player_id == MY_PLAYER_ID:
            # Update
            y, x = stdscr.getyx() # put cursor position in x and y
            if stdscr.inch(y, x) != ord(' '): #Check for Space
                continue

            stdscr.addstr(6, 0, 'Placed MY element')
            draw(y, x, stdscr, PLAYER_CH)
            board[y_pos][x_pos] = PLAYER_CH
            pos = y_pos * 3 + x_pos
            client.publish("tictactoe/server/"+str(GAME_ID)+"/move", str(pos))
            
            # Switch player
            RESPONS = False
            current_player_id = 0
            stdscr.refresh()
        else:
            stdscr.addstr(9, 0, "KeyID: " + str(key) + ", Key: " + str(ord(chr(key))) )
            stdscr.refresh()

            
        
    stdscr.refresh()
    stdscr.getkey()


if __name__ == '__main__':
    wrapper(main)
