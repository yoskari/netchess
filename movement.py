from constants import WHITE_UNITS, BLACK_UNITS

def move(start, target, board, score):
    sx, sy = start
    tx, ty = target
    unit = board[sy][sx]
    board[sy][sx] = 0
    if board[ty][tx] != 0:
        score += 1
    winner = ""
    if board[ty][tx] == 1:
        winner = "black"
    elif board[ty][tx] == 7:
        winner = "white"

    board[ty][tx] = unit
    return board, score, winner

def get_possible_moves(selected, board):
    def pawn_movement(moves=2):
        if friendly_units == WHITE_UNITS:
            for move_y in range(1, moves+1):
                if y + move_y > 7:
                    break
                squere = board[y+move_y][x]
                if squere != 0:
                    break
                if not squere in friendly_units:
                    possible_moves.append((x, y+move_y))
            positions = [(x+1, y+1), (x-1, y+1)]

        if friendly_units == BLACK_UNITS:
            for move_y in range(1, moves+1):
                if y - move_y < 0:
                    break
                squere = board[y-move_y][x]
                if squere != 0:
                    break
                if not squere in friendly_units:
                    possible_moves.append((x, y-move_y))
            positions = [(x+1, y-1), (x-1, y-1)]

        if x-1 > 0 and x+1 < 8:
            for pos_x, pos_y in positions:
                if board[pos_y][pos_x] != 0 and board[pos_y][pos_x] not in friendly_units:
                    possible_moves.append((pos_x, pos_y))

    def knight_movement():
        positions = [
            (x-2, y-1),
            (x-2, y+1),
            (x+2, y-1),
            (x+2, y+1),
            (x+1, y+2),
            (x-1, y+2),
            (x+1, y-2),
            (x-1, y-2),
        ]
        for pos_x, pos_y in positions:
            if 8 > pos_x >= 0 and 8 > pos_y >= 0:
                if board[pos_y][pos_x] not in friendly_units:
                    possible_moves.append((pos_x, pos_y))


    def non_diagonal(moves):
        for move_x in range(1, moves+1):
            if x + move_x > 7:
                break
            squere = board[y][x+move_x]
            if not squere in friendly_units:
                possible_moves.append((x+move_x, y))
            if squere != 0:
                break

        for move_x in range(1, moves+1):
            if x - move_x < 0:
                break
            squere = board[y][x-move_x]
            if not squere in friendly_units:
                possible_moves.append((x-move_x, y))
            if squere != 0:
                break

        for move_y in range(1, moves+1):
            if y + move_y > 7:
                break
            squere = board[y+move_y][x]
            if not squere in friendly_units:
                possible_moves.append((x, y+move_y))
            if squere != 0:
                break

        for move_y in range(1, moves+1):
            if y - move_y < 0:
                break
            squere = board[y-move_y][x]
            if not squere in friendly_units:
                possible_moves.append((x, y-move_y))
            if squere != 0:
                break
    def diagonal(moves):
        for move_x in range(1, moves+1):
            if x + move_x > 7 or y + move_x > 7:
                break
            squere = board[y+move_x][x+move_x]
            if not squere in friendly_units:
                possible_moves.append((x+move_x, y+move_x))
            if squere != 0:
                break

        for move_x in range(1, moves+1):
            if x - move_x < 0 or y + move_x > 7:
                break
            squere = board[y+move_x][x-move_x]
            if not squere in friendly_units:
                possible_moves.append((x-move_x, y+move_x))
            if squere != 0:
                break

        for move_y in range(1, moves+1):
            if y - move_y < 0 or x - move_y < 0:
                break
            squere = board[y-move_y][x-move_y]
            if not squere in friendly_units:
                possible_moves.append((x-move_y, y-move_y))
            if squere != 0:
                break

        for move_y in range(1, moves+1):
            if y - move_y < 0 or x + move_y > 7:
                break
            squere = board[y-move_y][x+move_y]
            if not squere in friendly_units:
                possible_moves.append((x+move_y, y-move_y))
            if squere != 0:
                break

    possible_moves = []
    x, y = selected
    selected_unit = board[y][x]
    if selected_unit in WHITE_UNITS:
        friendly_units = WHITE_UNITS
    elif selected_unit in BLACK_UNITS:
        friendly_units = BLACK_UNITS
    # pawn movement
    if selected_unit in [6, 12]:
        pawn_movement()
    elif selected_unit in [1, 7]:
        diagonal(1)
        non_diagonal(1)
    elif selected_unit in [2, 8]:
        diagonal(8)
        non_diagonal(8)
    elif selected_unit in [3, 9]:
        diagonal(8)
    elif selected_unit in [4, 10]:
        knight_movement()
    elif selected_unit in [5, 11]:
        non_diagonal(8)


    return possible_moves
