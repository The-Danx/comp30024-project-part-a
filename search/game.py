"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching

This module contains game logic.
"""

WIN = 'w'
LOSE = 'l'
DRAW = 'd'


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


def battle(u, l):
    """Return the outcome of a battle between an upper and lower token.
    WIN if tok1 defeats tok2, LOSE if tok2 is defeated by tok1 and DRAW if
    none is defeated.
    """
    if ((u == 'r' and l == 's') or
        (u == 'p' and l == 'r') or
            (u == 's' and l == 'p')):
        return WIN
    elif ((u == 's' and l == 'r') or
          (u == 'r' and l == 'p') or
          (u == 'p' and l == 's')):
        return LOSE
    else:
        return DRAW


def upper_wl_upper(which, up_vs_lo, i):
    """Return the list of indices of upper and lower tokens to be removed when
    up1 wins or loses with up2.  Parameter "which" is the index of upper
    token which won up_vs_up.
    """
    if up_vs_lo == WIN:
        # Lower token has same symbol as u2.
        # Other upper token and lower token defeated
        return [[int(not which)], [i]]
    elif up_vs_lo == LOSE:
        # up1, up2, and lower token all have different symbols
        return [[0, 1], [i]]  # All tokens defeated
    elif up_vs_lo == DRAW:
        # Only u2 is defeated
        return [[int(not which)], []]


def upper_d_upper(up_vs_lo, i):
    """Return a list of indices of upper and lower tokens to be removed when
    up1 draws with up2.
    """
    if up_vs_lo == WIN:
        return [[], [i]]  # Lower token is defeated
    elif up_vs_lo == LOSE:
        return [[0, 1], []]  # Both upper tokens are defeated
    elif up_vs_lo == DRAW:
        return [[], []]  # Nothing happens


def upper_vs_lower(which, u, l, tokens_defeated, i):
    """Return and append the defeated token to a list from a battle between an
    upper and lower token.
    """
    up_vs_lo = battle(u, l)
    if up_vs_lo == WIN:
        tokens_defeated[1].append(i)
    elif up_vs_lo == LOSE:
        tokens_defeated[0].append(int(not which))
    return tokens_defeated


def find_defeated_tokens(node):
    """Return a list that contains the indices of the upper and lower
    tokens to be removed.
    """
    tokens_defeated = [[], []]

    if len(node.upper) == 1:
        up = node.upper[0]
        # Find the index of the lower token defeated
        for i, lo in enumerate(node.lower):
            if (up[1], up[2]) == (lo[1], lo[2]):
                # The upper token always defeats the lower token
                # at this point anyway, since game specifications
                # says the game will always be winnable
                return [[], [i]]
        return tokens_defeated  # Will be empty list

    elif len(node.upper) == 2:
        up1 = node.upper[0]
        up2 = node.upper[1]

        for i, lo in enumerate(node.lower):

            # If both upper tokens share the same hex as lower token
            if (up1[1], up1[2]) == (lo[1], lo[2]) and \
               (up2[1], up2[2]) == (lo[1], lo[2]):

                up_vs_up = battle(up1[0], up2[0])
                up_vs_lo = battle(up1[0], lo[0])

                if up_vs_up == WIN:
                    return upper_wl_upper(0, up_vs_lo, i)
                elif up_vs_up == LOSE:
                    return upper_wl_upper(1, up_vs_lo, i)
                elif up_vs_up == DRAW:
                    return upper_d_upper(up_vs_lo, i)

            elif (up1[1], up1[2]) == (lo[1], lo[2]):
                tokens_defeated = upper_vs_lower(0, up1[0], lo[0],
                                                 tokens_defeated, i)
            elif (up2[1], up2[2]) == (lo[1], lo[2]):
                tokens_defeated = upper_vs_lower(1, up2[0], lo[0],
                                                 tokens_defeated, i)

        return tokens_defeated


def winning_symbol(up):
    """Return the symbol that is defeated by up."""
    if up == "r":
        return "s"
    elif up == "s":
        return "p"
    elif up == "p":
        return "r"


def print_move(path, turn):
    """Print out a move based upon the specification outline."""
    print("Turn %d: SLIDE from (%d,%d) to (%d,%d)" % (-turn + len(path),
                                                      path[turn][0][1], path[turn][0][2], path[turn - 1][0][1],
                                                      path[turn - 1][0][2]))
