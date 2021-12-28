import socket
import random
import pygame
import pickle
from threading import Thread
from functions import print_text
from constants import *

# server's IP address
# if the server is not on this machine,
# put the private (network) IP address (e.g 192.168.1.2)
SERVER_HOST = input("server ip: ")
SERVER_PORT = 9123 # server's port
separator_token = "<SEP>" # we will use this to separate the client name & message

# initialize TCP socket
s = socket.socket()
print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
# connect to the server
s.connect((SERVER_HOST, SERVER_PORT))
print("[+] Connected.")
client_id = input("name: ")

def listen_for_messages():
    global board, selected, score, possible_moves, turn
    while True:
        msg = s.recv(1024)
        msg = pickle.loads(msg)
        print(msg)
        if type(msg) == dict:
            board = msg["board"]
            selected = msg["selected"]
            score = msg["score"]
            possible_moves = msg["possible_moves"]
            turn = msg["turn"]

# make a thread that listens for messages to this client & print them
t = Thread(target=listen_for_messages)
# make the thread daemon so it ends whenever the main thread ends
t.daemon = True
# start the thread
t.start()

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Chess")
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

board_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
board_tile.fill(LIGHT)
board_rect = (70, 70, DISPLAY_W, DISPLAY_H)
selected = ()
selection_rect = pygame.Rect(0, 0, 80, 80)

possible_moves = []
turn = "white"
friendly_units = WHITE_UNITS
score = {
    "white": 0,
    "black": 0,
}

white = True

while True:
    for event in pygame.event.get():
        if event == pygame.QUIT:
            s.close()
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                msg = f"{client_id}<SEP>{mouse_x},{mouse_y}"
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

        screen.blit(display, (70, 70))
        for i in range(8):
            print_text(f"{i}", 40, 90+i*80, screen)
        for i in range(8):
            print_text(f"{i}", 100+i*80, 30, screen)

        print_text(f"White score: {score['white']}", 0, 750, screen, 0)
        print_text(f"Black score: {score['black']}", 800, 750, screen, 2)
        print_text(f"Turn: {turn}", 400, 750, screen, 1)
        pygame.display.update()
        clock.tick(30)
