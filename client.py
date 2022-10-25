import socket
import select
import sys
import random
import pygame
import pickle
from constants import *

def victory(winner, screen, s, client_id):
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    # continue game
                    screen.fill(WHITE)
                    print_text("Waiting for the other player...", 400, 400, screen, 1, 64, BLACK)
                    pygame.display.update()
                    s.send("reset".encode())
                    game(s, client_id)
                if event.key == pygame.K_q:
                    s.close()
                    pygame.quit()
                    sys.exit(0)
            if event.type == pygame.QUIT:
                s.close()
                pygame.quit()
                sys.exit(0)
        print_text("Checkmate!", 400, 400, screen, 1, 64, WHITE)
        print_text("Checkmate!", 402, 402, screen, 1, 64, BLACK)
        print_text(f"{winner} has won the game.", 400, 464, screen, 1, 32, WHITE)
        print_text(f"{winner} has won the game.", 402, 466, screen, 1, 32, BLACK)
        print_text(f"Press", SCREEN_W // 2, SCREEN_H - 150, screen, 1, 48, BLACK)
        print_text(f"C to play again", 0, SCREEN_H - 100, screen, 0, 32, BLACK)
        print_text(f"Q to quit", SCREEN_H, SCREEN_H - 100, screen, 2, 32, BLACK)
        pygame.display.update()
        clock.tick(30)

def print_text(text, x, y, display, allignment=0, size=32, color=BLACK):
    """
    Draws text onto the screen
    allignments: 0=left, 1=center, 2=right
    Args:
        text
        x
        y
        display: surface to draw on
        allignment: 0=left, 1=center, 2=right (default=0)
        size: font size
        color: text color
    """
    font = pygame.font.SysFont("Helvetica", size)
    surf = font.render(text, False, color)
    if allignment == 1:
        x = x - surf.get_width() / 2
    elif allignment == 2:
        x = x - surf.get_width()
    display.blit(surf, (x, y))

def game(s, client_id):
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

    pygame.event.set_blocked([pygame.MOUSEMOTION])
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                s.close()
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    s.close()
                    sys.exit(0)
    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # send click data
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
            victory(winner, screen, s, client_id)

        screen.blit(display, (70, 70))
        for i in range(8):
            print_text(f"{i}", 40, 90+i*80, screen)
        for i in range(8):
            print_text(f"{i}", 100+i*80, 30, screen)

        #for i, keyvalue in enumerate(score.items()):
        #    key, value = keyvalue
        #    if i == 0:
        #        print_text(f"{key}'s score: {value}", 0, 750, screen, 0)
        #    elif i == 1:
        #        print_text(f"{key}'s score: {value}", 800, 750, screen, 2)
        print_text(f"Turn: {turn}", 400, 750, screen, 1)
        print_text(f"fps: {int(clock.get_fps())}", 0, 0, screen, 0)
        pygame.display.update()
        clock.tick(30)

        # netcode (receiving game data)
        ready = select.select([s], [], [], 0.01)
        if ready[0]:
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

def main():
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
    game(s, client_id)

if __name__ == "__main__":
    main()
