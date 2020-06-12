#!/usr/bin/python3

import curses
from curses import wrapper
import time
import paho.mqtt.client as mqtt

#Player characters
P1_CH = 'X'
P2_CH = 'O'
#Move field
X_MOVE = 4
Y_MOVE = 2
#Board location
X_OFFSET = 1
Y_OFFSET = 4

RESPONS = False
X_RESPONS = 1
Y_RESPONS = 1

GAME_ID = 0
MY_PLAYER_ID = 0
OPPONENT_PLAYER_ID = 0
CURRENT_PLAYER_ID = 1

def on_connect(client, userdata, flags, rc):
    # print("Connected with result code "+str(rc))
    client.subscribe("tictactoe/delegation")
    client.publish("tictactoe/request/delegation","join")

def on_message(client, userdata, msg):
    global MY_PLAYER_ID, GAME_ID, RESPONS, X_RESPONS, Y_RESPONS, CURRENT_PLAYER_ID
    msg.payload = msg.payload.decode("utf-8")
    #Get player ID
    if msg.topic == "tictactoe/delegation":
        if MY_PLAYER_ID == 0:
            MY_PLAYER_ID = int(msg.payload)
            client.subscribe("tictactoe/delegation/" + str(MY_PLAYER_ID))

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
        # client.publish("tictactoe/info", "game id : "+ str(GAME_ID))
        
    #Action
    elif msg.topic == "tictactoe/server/"+str(GAME_ID)+"/move/"+str(OPPONENT_PLAYER_ID):
        # client.publish("tictactoe/info", "info: "+ str(msg.payload))
        x = msg.payload % 3
        y = (msg.payload - x)/3
        X_RESPONS = x
        Y_RESPONS = y
        RESPONS = True

    #Still connected check
    elif msg.topic == "tictactoe/player/"+str(MY_PLAYER_ID)+"/connected":
        client.publish("tictactoe/connected", str(MY_PLAYER_ID))


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
def draw(y, x, stdscr, player_id):
    stdscr.addch(y, x, P2_CH if player_id % 2 else P1_CH)

#stdscr - default window
def main(stdscr):
    global RESPONS, CURRENT_PLAYER_ID, MY_PLAYER_ID, OPPONENT_PLAYER_ID
    # Clear screen
    # stdscr.clear()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("93.166.88.200", 1883, 60)
    client.loop_start()
    
    draw_board(stdscr)
    #player who starts
    player_id = 0

    x_pos = 1
    y_pos = 1
    board = [list('   ') for _ in range(3)]

          
    while True:
        stdscr.move(Y_OFFSET + y_pos * Y_MOVE, X_OFFSET + x_pos * X_MOVE)

        #Check for opponent move
        if CURRENT_PLAYER_ID == OPPONENT_PLAYER_ID and RESPONS == True:
            x = int(X_RESPONS) * X_MOVE + X_OFFSET
            y = int(Y_RESPONS) * Y_MOVE + Y_OFFSET
            draw(y, x, stdscr, player_id)
            board[y_pos][x_pos] = P1_CH if OPPONENT_PLAYER_ID % 2 else P2_CH
            RESPONS = False
            CURRENT_PLAYER_ID = MY_PLAYER_ID
            stdscr.refresh()
        
        #Check for my move.
        elif CURRENT_PLAYER_ID == MY_PLAYER_ID:
            #Show cursor
            curses.curs_set(1)
            
            #Get key char
            key = stdscr.getch()

            #Check keystrokes
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
            elif key == ord(' ') and CURRENT_PLAYER_ID == MY_PLAYER_ID:
                y, x = stdscr.getyx()
                client.publish("tictactoe/info", "x place: "+ str(x))
                client.publish("tictactoe/info", "y place: "+ str(y))
                if stdscr.inch(y, x) != ord(' '): #Check for Space
                    continue
                
                draw(y, x, stdscr, player_id)
                board[y_pos][x_pos] = P2_CH if CURRENT_PLAYER_ID % 2 else P1_CH
                stdscr.refresh()

                pos = y_pos * 3 + x_pos
                client.publish("tictactoe/server/"+str(GAME_ID)+"/move/"+str(MY_PLAYER_ID), str(pos))
                
                # Switch player
                CURRENT_PLAYER_ID = OPPONENT_PLAYER_ID
                curses.curs_set(0)

            #stdscr.refresh()
            #stdscr.getkey()
        
    stdscr.refresh()
    stdscr.getkey()


if __name__ == '__main__':
    wrapper(main)
