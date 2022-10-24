import socket
import sys
import random
import pygame
import pickle
from threading import Thread
from functions import print_text, victory
from constants import *

def main():
    def listen_for_messages():
        nonlocal s, board, selected, score, possible_moves, turn, winner
        while True:
            msg = s.recv(1024)
            try:
                msg = pickle.loads(msg)
            except Exception as e:
                print(e)
                print("Quitting...")
                pygame.quit()
                sys.exit(1)
            if type(msg) == dict:
                print("Got game data")
                print(msg)
                board = msg["board"]
                selected = msg["selected"]
                score = msg["score"]
                possible_moves = msg["possible_moves"]
                turn = msg["turn"]
                winner = msg["winner"]
            else:
                print("Got invalid data")
                print(msg)
    SERVER_HOST = input("server ip: ")
    SERVER_PORT = 9123
    separator_token = "<SEP>"
    
    # initialize TCP socket
    s = socket.socket()
    print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
    # connect to the server
    s.connect((SERVER_HOST, SERVER_PORT))
    print("[+] Connected.")
    #client_id = input("name: ")
    client_id = input("name: ")
    
    s.send(client_id.encode())
    print("waiting for the other player to join...")
    while True:
        try:
            msg = s.recv(1024)
            msg = pickle.loads(msg)
            if type(msg) == dict:
                board = msg["board"]
                selected = msg["selected"]
                score = msg["score"]
                possible_moves = msg["possible_moves"]
                turn = msg["turn"]
            break
        except Exception as e:
            print(e)
    
    # make a thread that listens for messages to this client & print them
    t = Thread(target=listen_for_messages)
    # make the thread daemon so it ends whenever the main thread ends
    t.daemon = True
    # start the thread
    t.start()
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption(f"Chess - {client_id}")
    display = pygame.Surface((DISPLAY_W, DISPLAY_H))
    clock = pygame.time.Clock()
    
    unit_map = pygame.image.load("units.png")
    images = []
    for y in range(2):
        for x in range(6):
            surf = pygame.Surface((80, 80))
            surf.blit(unit_map, (0, 0), (80*x, 80*y, 80, 80))
            surf.set_colorkey(MAGENTA)
            images.append(surf)
    
    board_squeres = []
    for x in range(8):
        for y in range(8):
            board_squeres.append(pygame.Rect(70+x*80, 70+y*80, 80, 80))
    
    board_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
    board_tile.fill(LIGHT)
    board_rect = (70, 70, DISPLAY_W, DISPLAY_H)
    selection_rect = pygame.Rect(0, 0, 80, 80)
    winner = ""
    
    color = turn.split(" - ")[1]
    if color == "white":
        friendly_units = WHITE_UNITS
    else:
        friendly_units = BLACK_UNITS
    
    white = True
    pygame.event.set_blocked(None)
    pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN])
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                s.close()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    s.close()
                    pygame.quit()
                    sys.exit(0)
    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    msg = f"{client_id}<SEP>{mouse_x},{mouse_y}"
                    print("sending: ", msg)
                    s.send(msg.encode())
    
            screen.fill(WHITE)
            display.fill(DARK)
    
            for y, row in enumerate(board):
                for x, squere in enumerate(row):
                    white = not white
                    if white:
                        display.blit(board_tile, (x*TILE_SIZE, y*TILE_SIZE))
                    if squere != 0:
                        display.blit(images[squere-1], (x*TILE_SIZE, y*TILE_SIZE))
                white = not white
    
            if selected != ():
                selection_rect.x = selected[0]*80
                selection_rect.y = selected[1]*80
                pygame.draw.rect(display, BLACK, selection_rect, 2)
    
            for pmove in possible_moves:
                move_rect = pygame.Rect(pmove[0]*80, pmove[1]*80, 80, 80)
                pygame.draw.rect(display, GREEN, move_rect, 2)
    
            if winner != "":
                victory(winner, screen)
    
            screen.blit(display, (70, 70))
            for i in range(8):
                print_text(f"{i}", 40, 90+i*80, screen)
            for i in range(8):
                print_text(f"{i}", 100+i*80, 30, screen)
    
            for i, keyvalue in enumerate(score.items()):
                key, value = keyvalue
                if i == 0:
                    print_text(f"{key}'s score: {value}", 0, 750, screen, 0)
                elif i == 1:
                    print_text(f"{key}'s score: {value}", 800, 750, screen, 2)
            print_text(f"Turn: {turn}", 400, 750, screen, 1)
            pygame.display.update()
            clock.tick(30)

if __name__ == "__main__":
    main()
