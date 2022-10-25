import random
import socket
import sys
import pickle
import pygame
from threading import Thread
from constants import *
from movement import *

HOST = '0.0.0.0'
PORT = 9123
NUM_PLAYERS = 2

running = True
reset = 0

def main():
    global reset
    def listen_for_client(cs):
        global running, reset
        nonlocal selected, board, possible_moves, turn, friendly_units, \
                 score, board_squares, player_turn, winner
        """
        This function keep listening for a message from `cs` socket
        Whenever a message is received, broadcast it to all other connected clients
        """
        while True:
            if not running:
                break
            try:
                # keep listening for a message from `cs` socket
                msg = cs.recv(1024).decode()
                print("Got: ", msg)
                if msg == "reset":
                    reset += 1
                    continue
            except Exception as e:
                # client no longer connected
                # remove it from the set
                print(f"[!] Error: {e}")
                client_sockets.remove(cs)
            else:
                try:
                    sender, coordinates = msg.split("<SEP>")
                except:
                    print("Player disconnected. Quitting...")
                    running = False
                    break
                if sender != player_turn:
                    continue
                mousepos = tuple([int(i) for i in coordinates.split(",")])

                target = ()
                for square in board_squares:
                    if square.collidepoint(mousepos):
                        target = (square.x // 80, square.y // 80)
                if target != ():
                    print(f"target: {target}")
                    if selected == ():
                        print("no tile selected, selecting...")
                        if board[target[1]][target[0]] != 0 and board[target[1]][target[0]] in friendly_units:
                            selected = target
                            possible_moves = get_possible_moves(selected, board)
                    else:
                        print(f"possible moves: {possible_moves}")
                        print(f"target in possible moves? {target in possible_moves}")
                        if target in possible_moves:
                            board, score[player_turn], winner = move(selected, target, board, score[player_turn])
                            possible_moves = []
                            if turn == "white":
                                turn = "black"
                                friendly_units = BLACK_UNITS
                            else:
                                turn = "white"
                                friendly_units = WHITE_UNITS
                            if player_turn == players[0]:
                                player_turn = players[1]
                            else:
                                player_turn = players[0]
                        else:
                            possible_moves = []
                        selected = ()
                msg = {
                    "board": board,
                    "selected": selected,
                    "score": score,
                    "possible_moves": possible_moves,
                    "turn": player_turn + " - " + turn,
                    "winner": winner,
                }
                # iterate over all connected sockets
                for i, client_socket in enumerate(client_sockets):
                    print("sending game data to:", players[i])
                    # and send the message
                    client_socket.sendall(pickle.dumps(msg))
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
    board_squares = []
    for x in range(8):
        for y in range(8):
            board_squares.append(pygame.Rect(70+x*80, 70+y*80, 80, 80))
    selected = ()

    possible_moves = []
    turn = "white"
    player_turn = ""
    players = []
    friendly_units = WHITE_UNITS
    score = {}
    winner = ""
    # initialize list/set of all connected client's sockets
    client_sockets = set()
    # create a TCP socket
    s = socket.socket()
    # make the port as reusable port
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind the socket to the address we specified
    s.bind((HOST, PORT))
    # listen for upcoming connections
    s.listen(NUM_PLAYERS)
    print(f"[*] Listening as {HOST}:{PORT}")
    for i in range(NUM_PLAYERS):
        client_socket, client_address = s.accept()
        print(f"[+] {client_address} connected.")
        playername = client_socket.recv(64).decode()
        if player_turn == "":
            player_turn = playername
        score[playername] = 0
        players.append(playername)
        # add the new connected client to connected sockets
        client_sockets.add(client_socket)
        # start a new thread that listens for each client's messages
        t = Thread(target=listen_for_client, args=(client_socket,))
        # make the thread daemon so it ends whenever the main thread ends
        t.daemon = True
        # start the thread
        t.start()
        if len(client_sockets) > 1:
            print("starting game")
            msg = {
                "board": board,
                "selected": selected,
                "score": score,
                "possible_moves": possible_moves,
                "turn": player_turn + " - " + turn,
            }
            for client_socket in client_sockets:
                client_socket.send(pickle.dumps(msg))

    while running:
        # restart the game if got two reset messages
        if reset >= 2:
            reset = 0
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
            selected = ()
            possible_moves = []
            player_turn = players[random.randint(0, 1)]
            turn = player_turn + " - white"
            score = {}
            friendly_units = WHITE_UNITS
            for name in players:
                score[name] = 0
            winner = ""
            msg = {
                "board": board,
                "selected": selected,
                "score": score,
                "possible_moves": possible_moves,
                "turn": turn,
                "winner": winner,
            }
            for client_socket in client_sockets:
                client_socket.send(pickle.dumps(msg))

    # close client sockets
    for cs in client_sockets:
        cs.close()
    # close server socket
    s.close()

if __name__ == "__main__":
    main()
