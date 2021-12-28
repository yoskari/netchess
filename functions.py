import pygame
from constants import BLACK, WHITE

def victory(winner, screen):
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                from main import main
                main()

        print_text("Checkmate!", 400, 400, screen, 1, 64, WHITE)
        print_text("Checkmate!", 402, 402, screen, 1, 64, BLACK)
        print_text(f"{winner} has won the game.", 400, 464, screen, 1, 32, WHITE)
        print_text(f"{winner} has won the game.", 402, 466, screen, 1, 32, BLACK)
        pygame.display.update()
        clock.tick(30)

def print_text(text, x, y, display, allignment=0, size=32, color=BLACK): # pragma: no cover
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
