import pygame
import sys
from constants import *
from movement import *
from functions import *

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


def main():
# white units
# 1: king
# 2: queen
# 3: bishop
# 4: knight
# 5: rook
# 6: pawn

# black units
# 7: king
# 8: queen
# 9: bishop
# 10: knight
# 11: rook
# 12: pawn
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
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                victory(turn, screen)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mousepos = pygame.mouse.get_pos()
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
