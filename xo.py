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

MY_PLAYER_ID = 0
LAST_MOVE = 1


def on_connect(client, userdata, flags, rc):
    # print("Connected with result code "+str(rc))
    client.subscribe("tictactoe/delegation")
    client.subscribe("tictactoe/move/+")
    client.publish("tictactoe/request/delegation","join")

def on_message(client, userdata, msg):
    msg.payload = msg.payload.decode("utf-8")
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == "tictactoe/move/0":
        print("Placing an X")
    elif msg.topic == "tictactoe/move/1":
        print("Placing an O")
    elif msg.topic == "tictactoe/delegation":
        MY_PLAYER_ID = int(msg.payload)
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
def draw(y, x, stdscr, player_id):
    stdscr.addch(y, x, P2_CH if player_id else P1_CH)

#stdscr - default window
def main(stdscr):
    # Clear screen
    # stdscr.clear()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("93.166.88.200", 1883, 60)
    client.loop_start()

    draw_board(stdscr)
    #player who starts
    current_player_id = 0

    x_pos = 1
    y_pos = 1
    board = [list('   ') for _ in range(3)]

    # while MY_PLAYER_ID == 2:
    #     time.sleep(0.1)


    global LAST_MOVE
    while True:
        stdscr.move(Y_OFFSET + y_pos * Y_MOVE, X_OFFSET + x_pos * X_MOVE)
        if current_player_id == MY_PLAYER_ID:
            if LAST_MOVE != 0:
                opponent = 0 if MY_PLAYER_ID == 1 else 1
                x = LAST_MOVE % 3
                y = int(LAST_MOVE / 3)
                draw(Y_OFFSET + y, X_OFFSET + x, stdscr, opponent)
                LAST_MOVE = 0

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
            elif key == ord(' '):
                # Update
                y, x = stdscr.getyx() # put cursor position in x and y
                if stdscr.inch(y, x) != ord(' '): #Check for Space
                    continue
                
                draw(y, x, stdscr, current_player_id)
                board[y_pos][x_pos] = P2_CH if current_player_id else P1_CH
                
                # Switch player
                current_player_id = (current_player_id + 1) % 2

    stdscr.refresh()
    stdscr.getkey()


if __name__ == '__main__':
    wrapper(main)
