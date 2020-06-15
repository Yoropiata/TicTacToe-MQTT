# #!/usr/bin/python3

import curses
from curses import wrapper
import time
import paho.mqtt.client as mqtt
import logging
import re

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
VICTORY = None


GAME_ID = None
MY_PLAYER_ID = None
CURRENT_PLAYER_ID = 1

def on_connect(client, userdata, flags, rc):
    client.subscribe("tictactoe/delegation")
    client.subscribe("tictactoe/delegation/gameserver")
    client.publish("tictactoe/request/playerid")

def on_message(client, userdata, msg):
    global MY_PLAYER_ID, GAME_ID, RESPONS, X_RESPONS, Y_RESPONS, MOVE, CURRENT_PLAYER_ID, VICTORY
    msg.payload = msg.payload.decode("utf-8")
    logging.info(msg.topic + ":data=" + msg.payload)
    #Give player ID and subscribe to player
    if msg.topic == "tictactoe/delegation":
        if MY_PLAYER_ID is None:
            MY_PLAYER_ID = int(msg.payload)
            CURRENT_PLAYER_ID = MY_PLAYER_ID if MY_PLAYER_ID % 2 == 1 else 0

            client.subscribe("tictactoe/player/"+str(MY_PLAYER_ID)+"/#")
            client.subscribe("tictactoe/player/"+str(MY_PLAYER_ID))
            client.subscribe("tictactoe/delegation/"+str(MY_PLAYER_ID))

            client.publish("tictactoe/request/gameserver", str(MY_PLAYER_ID))

    #Get game lobby
    elif msg.topic == "tictactoe/delegation/" + str(MY_PLAYER_ID):
        if GAME_ID is None:
            GAME_ID = int(msg.payload)
            client.subscribe("tictactoe/server/"+str(GAME_ID)+"/move/#")
            client.subscribe("tictactoe/server/"+str(GAME_ID)+"/victory")
        
    #Action
    elif msg.topic == "tictactoe/server/"+str(GAME_ID)+"/move/"+str(MY_PLAYER_ID):
        logging.info("User made a move.")
        return
    elif re.search("tictactoe/server/.+/move/.+", msg.topic):
        logging.info("Opponent made a move")
        client.publish("tictactoe/info", "info: "+ str(msg.payload))
        MOVE = int(msg.payload)
        x = MOVE % 3
        y = (MOVE - x)/3
        X_RESPONS = x
        Y_RESPONS = y
        RESPONS = True
    elif msg.topic == "tictactoe/server/"+str(GAME_ID)+"/victory":
        VICTORY = "Du vandt, tillykke!!!" if int(msg.payload) == MY_PLAYER_ID else "Du tabte, lul git gut!!!" 


#Draw Board
def draw_board(stdscr):
    stdscr.addstr(0, 0, 'Tic Tac Toe - Waiting for id')
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
    logging.basicConfig(filename="debug.log", level=logging.DEBUG)
    logging.info("------------------MAIN-----------------------")

    global RESPONS, MY_PLAYER_ID, GAME_ID, PLAYER_CH, OPPONENT_CH, CURRENT_PLAYER_ID, VICTORY

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("93.166.88.200", 1883, 60)
    client.loop_start()

    draw_board(stdscr)

    x_pos = 1
    y_pos = 1
    board = [list('   ') for _ in range(3)]

    stdscr.refresh()
    while MY_PLAYER_ID is None:
        time.sleep(1)
    
    PLAYER_CH = P1_CH if MY_PLAYER_ID % 2 else P2_CH
    OPPONENT_CH = P2_CH if MY_PLAYER_ID % 2 else P1_CH

    # Clear "- Waiting for id"
    stdscr.addstr(0, 11, " - Connected - id: " + str(MY_PLAYER_ID) + ". Waiting for lobby")
    stdscr.refresh()

    while GAME_ID is None:
        stdscr.addstr(0, 11, " - Connected - id: " + str(MY_PLAYER_ID) + ". Waiting for lobby...")
        stdscr.refresh()
        time.sleep(1)
    
    stdscr.addstr(0, 11, " - Connected - id: " + str(MY_PLAYER_ID) + ". Waiting for lobby..")
    stdscr.refresh()
    stdscr.addstr(0, 11+len(" - Connected - id: " + str(MY_PLAYER_ID)), ". lobby: " + str(GAME_ID) + "            ")
    stdscr.refresh()
          
    while True:
        stdscr.move(Y_OFFSET + y_pos * Y_MOVE, X_OFFSET + x_pos * X_MOVE)

        if VICTORY is not None:
            logging.info("VICTORY IS NOT NONE")
            stdscr.addstr(10, 0, VICTORY)
            stdscr.refresh()
            break

        if CURRENT_PLAYER_ID != MY_PLAYER_ID and RESPONS == True:
            x = int(X_RESPONS) * X_MOVE + X_OFFSET
            y = int(Y_RESPONS) * Y_MOVE + Y_OFFSET
            
            draw(y, x, stdscr, OPPONENT_CH)
            board[y_pos][x_pos] = OPPONENT_CH

            stdscr.refresh()
            CURRENT_PLAYER_ID = MY_PLAYER_ID
            RESPONS = False

        if CURRENT_PLAYER_ID != MY_PLAYER_ID:
            continue
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
        elif key == ord(' ') and CURRENT_PLAYER_ID == MY_PLAYER_ID:
            # Update
            y, x = stdscr.getyx() # put cursor position in x and y
            if stdscr.inch(y, x) != ord(' '): #Check for Space
                continue

            draw(y, x, stdscr, PLAYER_CH)
            board[y_pos][x_pos] = PLAYER_CH
            pos = y_pos * 3 + x_pos
            
            # Switch player
            RESPONS = False
            CURRENT_PLAYER_ID = 0
            stdscr.refresh()

            client.publish("tictactoe/server/"+str(GAME_ID)+"/move/" + str(MY_PLAYER_ID), str(pos))
        
    stdscr.refresh()
    stdscr.getkey()


if __name__ == '__main__':
    wrapper(main)
