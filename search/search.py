"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching

This module contains search logic.
"""

from collections import defaultdict
from copy import deepcopy
from itertools import product
from search.game import winning_symbol
from search.util import sign


class Node():

    def __init__(self, parent=None, upper=None, lower=None, block=None, defeatedTokensRemaining=None):
        """Initialise class variables."""
        self.parent = parent
        self.upper = upper
        self.lower = lower
        self.block = block
        self.neighbours = []
        self.g = 0  # Distance so far
        self.h = 0  # Distance to goal
        self.f = 0  # Total distance to goal from start
        self.defeatedTokensRemaining = defeatedTokensRemaining

    def get_neighbours(self):
        """Get all combinations of neighbours of the upper tokens"""
        new_positions = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
        n = len(self.upper)
        self.neighbours = []
        positions_dic = defaultdict(set)
        for combination in product(new_positions, repeat=n):
            neighbour = deepcopy(self.upper)
            for i in range(n):
                # Slide actions
                neighbour[i][1] = neighbour[i][1] + combination[i][0]
                neighbour[i][2] = neighbour[i][2] + combination[i][1]
                positions_dic[i].add(tuple(neighbour[i]))

            # Swing actions
            before = list(self.upper)
            for i, new_up in enumerate(neighbour):
                for old_up in before:
                    if (new_up[1], new_up[2]) == (old_up[1], old_up[2]):
                        # new_up can swing around old_up

                        count = 0
                        for direction in new_positions:
                            possible_swing = list(new_up)
                            possible_swing[1] = possible_swing[1] + \
                                direction[0]
                            possible_swing[2] = possible_swing[2] + \
                                direction[1]

                            if distance(possible_swing, before[i]) == 2:
                                valid_swing = list(neighbour)
                                valid_swing[i] = possible_swing
                                positions_dic[i].add(tuple(possible_swing))
                                count += 1

                            # Stop when we already found the 3 swing positions
                            if count == 3:
                                break

        # Get combinations of positions
        for i in list(product(*positions_dic.values(), repeat=1)):
            self.neighbours.append(list(map(list, i)))
        return 1


def calculate_h(node):
    """Calculate the estimated cost(h) for a node to reach its goal state.
     If there are multiple lower tokens, calculate the distance to the closest
    winning token, and then distance from that winning token to another
    winning token.  For example R -> s1 -> s2.
    """
    total_h = 0
    for up in node.upper:
        lower_toks = list(node.lower)
        upper_symbol = up[0]
        while len(lower_toks):
            h = []
            for lo in lower_toks:
                # Make sure we are only considering the "goal" lower tokens
                # with respect to the upper token
                if winning_symbol(upper_symbol) == lo[0]:
                    h.append(distance(up, lo))
                else:
                    h.append(float('inf'))  # infinite distance

            if all(x == float('inf') for x in h) and len(h) == len(lower_toks):
                # Means the upper token does not have any goal. In this case
                # its h value is 0
                break
            else:
                i = h.index(min(h))
                total_h += h[i]
                up = lower_toks.pop(i)

    return total_h


def distance(tok1, tok2):
    """Calculate the distance between two tokens."""
    dr = tok1[1] - tok2[1]
    dq = tok1[2] - tok2[2]

    if sign(dr) == sign(dq):
        return abs(dr+dq)
    else:
        return max(abs(dr), abs(dq))


def get_g_score(node, pq):
    """Check if the combination of upper tokens and lower tokens can be found
    in the priority queue; if yes, return the g-score of the similar node
    found in the priority queue.  Return - 1 if it is not present.  Priority
    queue has format[[f-score, node], ...].
    """
    nodes = [(n.upper, n.lower) for f, n in pq]

    try:
        # Find index i of the corresponding node, raise error if not found
        i = nodes.index((node.upper, node.lower))
        # Return the g-score of the i'th node in priority queue
        return [n.g for f, n in pq][i]
    except:
        return -1


def simple_h(tok1, tok2):
    """Return the estimated cost to reach tok2 from tok1."""
    dr = tok1[1] - tok2[1]
    dq = tok1[2] - tok2[2]

    if sign(dr) == sign(dq):
        return abs(dr+dq)
    else:
        return max(abs(dr), abs(dq))


def sort_priority_queue(pq):
    """Sort the priority queue by f-score.  Also puts node that have the
    least number of lower tokens at the front.  This ensures that the
    algorithm looks at states that are closer to the goal first.
    """

    pq = sorted(pq, key=lambda x: x[0])
    min_f = pq[0][0]  # Least f-score
    min_count = len(pq[0][1].lower)  # Least number of lower tokens
    best_i = 0  # Index of best node

    for i, j in enumerate(pq):
        if j[0] != min_f:
            break
        if len(j[1].lower) < min_count:
            min_count = len(j[1].lower)
            best_i = i

    # Swap the first node with the best node
    pq[0], pq[best_i] = pq[best_i], pq[0]
    return pq
