"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching

This script contains the entry point to the program (the code in
`__main__.py` calls `main()`). Your solution starts here!
"""

import sys
import json
import random

# If you want to separate your code into separate files, put them
# inside the `search` directory (like this one and `util.py`) and
# then import from them like this:
from util import print_board, print_slide, print_swing

def main():
    try:
        with open(sys.argv[1]) as file:
            data = json.load(file)
    except IndexError:
        print("usage: python3 -m search path/to/input.json", file=sys.stderr)
        sys.exit(1)

    # TODO:
    # Find and print a solution to the board configuration described
    # by `data`.
    # Why not start by trying to print this configuration out using the
    # `print_board` helper function? (See the `util.py` source code for
    # usage information).
    
    # Initialise game from input
    board_dict = {}
    for dat in data:
        for elem in data[dat]:
            if dat == 'upper':
                board_dict[elem[1], elem[2]] = [elem[0].upper()]
            elif dat == 'lower':
                board_dict[elem[1], elem[2]] = [elem[0]]
            else:
                board_dict[elem[1], elem[2]] = ['b']

    print_board(board_dict, message="Turn 0", compact=True, ansi=False)

    for i in range(1, 361):
        moves = []
        for location in board_dict:
            for piece in board_dict.get(location):
                if piece.islower() and piece != "b":
                    # Move logic
                    while True:
                        move = random.randint(0, 5)
                        if move == 0:
                            moves.append([board_dict, piece, location[0], location[1], location[0] + 1, location[1]])
                        elif move == 1:
                            moves.append([board_dict, piece, location[0], location[1], location[0], location[1] + 1])
                        elif move == 2:
                            moves.append([board_dict, piece, location[0], location[1], location[0] - 1, location[1] + 1])
                        elif move == 3:
                            moves.append([board_dict, piece, location[0], location[1], location[0] - 1, location[1]])
                        elif move == 4:
                            moves.append([board_dict, piece, location[0], location[1], location[0], location[1] - 1])
                        elif move == 5:
                            moves.append([board_dict, piece, location[0], location[1], location[0] + 1, location[1] - 1])
                        if isValidMove(board_dict, moves[-1][2], moves[-1][3], moves[-1][4], moves[-1][5]):
                            break
                        moves.pop()

        # Move processing
        for move in moves:
            moveToken(move[0], move[1], move[2], move[3], move[4], move[5], i)

        # print_board(board_dict, message="Turn " + str(i) + " - Pre-battle", compact=True, ansi=False)

        # Battling
        for location in board_dict:
            if len(board_dict.get(location)) >= 2:
                print_board(board_dict, message="Turn " + str(i) + " - Pre-battle", compact=True, ansi=False)
                rockPrescence = False
                paperPrescence = False
                scissorsPrescence = False
                for piece in board_dict.get(location):
                    if piece == "r" or piece == "R":
                        rockPrescence = True
                    elif piece == "p" or piece == "P":
                        paperPrescence = True
                    elif piece == "s" or piece == "S":
                        scissorsPrescence = True
                if rockPrescence and paperPrescence and scissorsPrescence:
                    board_dict.pop(location)
                else:
                    for piece in board_dict.get(location):
                        if (piece == "r" or piece == "R" and paperPrescence) or (piece == "p" or piece == "P" and scissorsPrescence) or (piece == "s" or piece == "S" and rockPrescence):
                            board_dict.get(location).remove(piece)
                print_board(board_dict, message="Turn " + str(i) + " - Post-battle", compact=True, ansi=False)

    
def isValidMove(board_dict, r_a, q_a, r_b, q_b):
    """
    Checks whether the given move is valid for the game. Does not assess whether the move is successful or a "correct" move.
    """
    # Check if move is off the board
    if r_b > 4 or r_b < -4 or q_b > 4 or q_b < -4:
        return False
    if r_b > 0 and q_b > 4 - r_b:
        return False
    if r_b < 0 and q_b < -4 - r_b:
        return False
    # Check if piece lands on block
    if board_dict.get((r_b, q_b)):
        for piece in board_dict.get((r_b, q_b)):
            if piece == "b":
                return False
    return True
                
def moveToken(board_dict, token, r_a, q_a, r_b, q_b, t):
    """
    Move tokens from one spot to another, updating the board_dict.
    """
    board_dict.get((r_a, q_a)).remove(token)
    if len(board_dict.get((r_a, q_a))) == 0:
        board_dict.pop((r_a, q_a))
    if board_dict.get((r_b, q_b)):
        board_dict.get((r_b, q_b)).append(token)
    else:
        board_dict[r_b, q_b] = [token]
    # print_slide(t, r_a, q_a, r_b, q_b)