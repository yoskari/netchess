import pygame
import socket
import sys
import pickle
from threading import Thread
from constants import *
from movement import *

HOST = '0.0.0.0'
PORT = 9123

board = [
    [5, 4, 3, 2, 1, 3, 4, 5],
    [6, 6, 6, 6, 6, 6, 6, 6],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [12,12,12,12,12,12,12,12],
    [11,10,9, 8, 7, 9, 10,11],
]
board_squeres = []
for x in range(8):
    for y in range(8):
        board_squeres.append(pygame.Rect(70+x*80, 70+y*80, 80, 80))

selected = ()

possible_moves = []
turn = "white"
friendly_units = WHITE_UNITS
score = {
    "white": 0,
    "black": 0,
}

# initialize list/set of all connected client's sockets
client_sockets = set()
# create a TCP socket
s = socket.socket()
# make the port as reusable port
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# bind the socket to the address we specified
s.bind((HOST, PORT))
# listen for upcoming connections
s.listen()
print(f"[*] Listening as {HOST}:{PORT}")

def listen_for_client(cs):
    global selected, board, possible_moves, turn, friendly_units, score, board_squeres
    """
    This function keep listening for a message from `cs` socket
    Whenever a message is received, broadcast it to all other connected clients
    """
    while True:
        try:
            # keep listening for a message from `cs` socket
            msg = cs.recv(1024).decode()
            print("Got: ", msg)
        except Exception as e:
            # client no longer connected
            # remove it from the set
            print(f"[!] Error: {e}")
            client_sockets.remove(cs)
        else:
            print("logic start")
            sender, coordinates = msg.split("<SEP>")
            mousepos = tuple([int(i) for i in coordinates.split(",")])

            target = ()
            for squere in board_squeres:
                if squere.collidepoint(mousepos):
                    target = (squere.x // 80, squere.y // 80)
            if target != ():
                if selected == ():
                    if board[target[1]][target[0]] != 0 and board[target[1]][target[0]] in friendly_units:
                        selected = target
                        possible_moves = get_possible_moves(selected, board)
                else:
                    if target in possible_moves:
                        board, score[turn], winner = move(selected, target, board, score[turn])
                        if winner != "":
                            victory(winner, screen)
                        possible_moves = []
                        if turn == "white":
                            turn = "black"
                            friendly_units = BLACK_UNITS
                        else:
                            turn = "white"
                            friendly_units = WHITE_UNITS
                    else:
                        possible_moves = []
                    selected = ()
            msg = {
                "board": board,
                "selected": selected,
                "score": score,
                "possible_moves": possible_moves,
                "turn": turn,
            }
            print("logic end")
            # iterate over all connected sockets
            for client_socket in client_sockets:
                print("sending game data to:")
                print(client_socket)
                # and send the message
                client_socket.send(pickle.dumps(msg))

while True:
    # we keep listening for new connections all the time
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} connected.")
    # add the new connected client to connected sockets
    client_sockets.add(client_socket)
    # start a new thread that listens for each client's messages
    t = Thread(target=listen_for_client, args=(client_socket,))
    # make the thread daemon so it ends whenever the main thread ends
    t.daemon = True
    # start the thread
    t.start()

# close client sockets
for cs in client_sockets:
    cs.close()
# close server socket
s.close()
