"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching

This module contains game logic.
"""

from collections import defaultdict


def distance(tok1, tok2):
    """Calculate the distance between two tokens."""
    dr = tok1[1] - tok2[1]
    dq = tok1[2] - tok2[2]

    if sign(dr) == sign(dq):
        return abs(dr+dq)
    else:
        return max(abs(dr), abs(dq))


def remove_defeated_tokens(node):
    """Update a node by removing all defeated tokens."""
    # key: (r,q) and value: list of tokens on (r,q)
    board_dict = defaultdict(list)

    # Fill board_dict
    for up in list(node.upper):
        board_dict[(up[1], up[2])].append(up[0])
    for lo in list(node.lower):
        board_dict[(lo[1], lo[2])].append(lo[0])

    for loc, symbols in board_dict.items():
        present = set([i for i in symbols])
        winner = ''  # Winning symbol at each loc

        if present == {'r', 'p', 's'}:
            pass  # Winner stays empty i.e. no winner
        elif len(present) == 1:
            winner = present.pop()
        else:
            # Two symbols fight, get one winner
            present = list(present)
            if win(present[0], present[1]):
                winner = present[0]
            else:
                winner = present[1]

        board_dict[loc] = winner  # Store the winner at each loc

    # Remove tokens that are defeated by winner
    for up in node.upper[::-1]:
        if up[0] != board_dict[(up[1], up[2])]:
            node.upper.remove(up)
    for lo in node.lower[::-1]:
        if lo[0] != board_dict[(lo[1], lo[2])]:
            node.lower.remove(lo)

    return 1


def sign(num):
    """Return the sign of a number."""
    if num < 0:
        return -1
    else:
        return 1
        

def simple_h(tok1, tok2):
    """Return the estimated cost to reach tok2 from tok1."""
    dr = tok1[1] - tok2[1]
    dq = tok1[2] - tok2[2]

    if sign(dr) == sign(dq):
        return abs(dr+dq)
    else:
        return max(abs(dr), abs(dq))


def valid_position(node):
    """Return true if the position is not blocked by a block
    token and is inside range of the board.
    """
    ran = range(-4, +4+1)
    valids = [rq for rq in [(r, q) for r in ran for q in ran if -r-q in ran]]
    blocks = [(i[1], i[2]) for i in node.block]
    valids = [pos for pos in valids if pos not in blocks]

    for up in node.upper:
        tok = (up[1], up[2])
        if tok not in valids:
            return 0
    return 1


def win(s1, s2):
    """Return true if s1 defeats s2, false otherwise."""
    if ((s1 == 'r' and s2 == 's') or
        (s1 == 'p' and s2 == 'r') or
            (s1 == 's' and s2 == 'p')):
        return True
    return False


def winning_symbol(up):
    """Return the symbol that is defeated by up."""
    if up == "r":
        return "s"
    elif up == "s":
        return "p"
    elif up == "p":
        return "r"