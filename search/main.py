"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching

This script contains the entry point to the program (the code in
`__main__.py` calls `main()`). Your solution starts here!
"""

import sys
import json
from copy import deepcopy
from itertools import product, permutations
from collections import defaultdict

# If you want to separate your code into separate files, put them
# inside the `search` directory (like this one and `util.py`) and
# then import from them like this:
from search.util import print_board, print_slide, print_swing

class Node():

    def __init__(self, parent=None, upper=None, lower=None, block=None):

        self.parent = parent
        self.upper = upper
        self.lower = lower
        self.block = block
        self.neighbours = []
        self.g = 0  # Distance so far
        self.h = 0  # Distance to goal
        self.f = 0  # Total distance to goal from start

    def get_neighbours(self):
        """Get all combinations of neighbours of the upper tokens"""
        new_positions = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
        n = len(self.upper)
        self.neighbours = []
        positions_dic = defaultdict(set)
        for combination in product(new_positions, repeat=n):
            neighbour = deepcopy(self.upper)
            for i in range(n):
                # slide actions
                neighbour[i][1] = neighbour[i][1] + combination[i][0]
                neighbour[i][2] = neighbour[i][2] + combination[i][1]
                positions_dic[i].add(tuple(neighbour[i])) 

            # swing actions
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

                            # stop when we already found the 3 swing positions
                            if count == 3:
                                break

        # get combinations of positions
        for i in list(product(*positions_dic.values(), repeat=1)):
            self.neighbours.append(list(map(list,i)))
        return 1

def valid_position(node):
    """valid_position returns true if the position is not blocked by a block 
    token and is inside range of the board"""
    
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
    # Return true if s1 defeats s2, false otherwise
    if ((s1 == 'r' and s2 =='s') or 
        (s1 == 'p' and s2 =='r') or 
        (s1 == 's' and s2 =='p')):
        return True 
    return False

def remove_defeated_tokens(node):
    """Return a list that contains the indices of the upper and lower 
    tokens to be removed"""
    
    # key: (r,q) and value: list of tokens on (r,q)
    board_dict = defaultdict(list) 

    # fill board_dict
    for up in list(node.upper):
        board_dict[(up[1], up[2])].append(up[0])
    for lo in list(node.lower):
        board_dict[(lo[1], lo[2])].append(lo[0])

    for loc, symbols in board_dict.items():
        present = set([i for i in symbols])
        winner = ''  # winning symbol at each loc

        if present == {'r', 'p', 's'}:
            pass  # winner stays empty i.e. no winner
        elif len(present) == 1:
            winner = present.pop()
        else:
            # two symbols fight, get one winner
            present = list(present)
            if win(present[0], present[1]):
                winner = present[0]
            else:
                winner = present[1]

        board_dict[loc] = winner  # store the winner at each loc

    # remove tokens that are defeated by winner
    for up in node.upper[::-1]:
        if up[0] != board_dict[(up[1], up[2])]:
            node.upper.remove(up)
    for lo in node.lower[::-1]:
        if lo[0] != board_dict[(lo[1], lo[2])]:
            node.lower.remove(lo)
        
    return 1

def sign(num):
    # sign function
    if num < 0: 
        return -1
    else:
        return 1

def distance(tok1, tok2):
    # get the number of steps to reach from tok1 to tok2
    dr = tok1[1] - tok2[1]
    dq = tok1[2] - tok2[2]

    if sign(dr) == sign(dq):
        return abs(dr+dq)
    else:
        return max(abs(dr), abs(dq)) 

def winning_symbol(up):
    # winning_symbol returns the symbol that is defeated by up
    if up == "r":
        return "s"
    elif up == "s":
        return "p"
    elif up == "p":
        return "r"

def calculate_h(node):
    """calculate the estimated cost (h) for a node to reach its goal state. 
    If there are multiple lower tokens, calculate the distance to the closest
    winning token, and then distance from that winning token to another winning 
    token. In other words, for example R -> s1 -> s2 """
    
    total_h = 0
    for up in node.upper:
        lower_toks = list(node.lower)
        upper_symbol = up[0]
        while len(lower_toks):
            h = []
            for lo in lower_toks:
                # make sure we are only considering the "goal" lower tokens
                # with respect to the upper token 
                if winning_symbol(upper_symbol) == lo[0]:
                    h.append(distance(up, lo))
                else:
                    h.append(float('inf')) # infinite distance
            
            if all(x==float('inf') for x in h) and len(h)==len(lower_toks):
                # means the upper token does not have any goal. In this case
                # its h value is 0 
                break
            else:
                i = h.index(min(h))
                total_h += h[i]
                up = lower_toks.pop(i)
    
    return total_h

def get_board_dict(data):
    
    """ get_board_dict converts the data dictionary into a format
     that is used by the print_board function """

    board_dict = {}
    for type, tokens in data.items():

        if type == "upper":
            for tok in tokens:
                board_dict[(tok[1], tok[2])] = "({})".format(tok[0].upper())
        elif type == "lower":
            for tok in tokens:
                board_dict[(tok[1], tok[2])] = "({})".format(tok[0])
        else:
            for tok in tokens: 
                board_dict[(tok[1], tok[2])] = "(X)"
    return board_dict

def get_g_score(node, pq):
    """ Priority queue has format [[f-score, node], ...]. get_g_score 
    checks if the combination of upper tokens and lower tokens can be found in 
    the priority queue; and if yes, returns the g-score of the similar node 
    found in the priority queue. It returns -1 if it is not present """
    nodes = [(n.upper, n.lower) for f, n in pq]

    try:
        # find index i of the corresponding node, raise error if not found
        i = nodes.index((node.upper, node.lower))
        # return the g-score of the i'th node in priority queue 
        return [n.g for f, n in pq][i]
    except:
        return -1

def sort_priority_queue(pq):
    """sorts the priority queue by f-score. Also puts node that have the 
    least number of lower tokens at the front. This ensures that the 
    algorithm looks at states that are closer to the goal first"""

    pq = sorted(pq, key=lambda x: x[0])
    min_f = pq[0][0]  # least f-score
    min_count = len(pq[0][1].lower)  # least number of lower tokens
    best_i = 0  # index of best node

    for i, j in enumerate(pq):
        if j[0] != min_f:
            break
        if len(j[1].lower) < min_count:
            min_count = len(j[1].lower)
            best_i = i

    # swap the first node  with the best node
    pq[0], pq[best_i] = pq[best_i], pq[0] 
    return pq


def main():

    try:
        with open(sys.argv[1]) as file:
            data = json.load(file)
    except IndexError:
        print("usage: python3 -m search path/to/input.json", file=sys.stderr)
        sys.exit(1)
    
    print(data)
    print_board(get_board_dict(data), compact=False, ansi=True)
    
    # Create start and end node
    start_node = Node(None, data['upper'], data['lower'], data['block'])

    # Initialise lists for open and closed nodes
    priority_queue = [[start_node.f, start_node]]  # [f-score, node]
    closed_list = []

    while len(priority_queue) > 0:

        priority_queue = sort_priority_queue(priority_queue)
        curr_node = priority_queue[0][1]
        if not curr_node.lower:
            print("Number of steps required: ", curr_node.g)
            # print_priority_queue(priority_queue)

            # retrace path 
            path = []
            while curr_node != start_node:
                path.append(curr_node.upper)
                curr_node = curr_node.parent
            path.append(start_node.upper)
            break
        
        # Remove node from priority queue and add to list of visited nodes
        priority_queue.pop(0) 
        closed_list.append(curr_node)

        # do not further explore node if all upper tokens are defeated
        if not curr_node.upper:
            continue

        curr_node.get_neighbours()
        for neighbour in curr_node.neighbours:

            # Create (temporary) child node
            child_node = Node(curr_node, neighbour, list(curr_node.lower), 
                              list(curr_node.block))
            
            # check if the position is valid (not blocked or out of bounds)
            if not valid_position(child_node):
                continue
            
            child_g_score = curr_node.g + 1

            # Record g and f score and add to priority queue
            child_node.g = child_g_score
            child_node.h = calculate_h(child_node)
            child_node.f = child_node.g + child_node.h

            remove_defeated_tokens(child_node) 
            
            if child_node in closed_list:
                # Node already visited
                continue 

            if get_g_score(child_node, priority_queue) == -1:
                pass
            else:
                # Check if the child is present in the priority queue. If yes,
                # check if we will need to update the g-score
                continue

            priority_queue.append([child_node.f, child_node])
        
    # for i in path[::-1]:
    #     print(i)

    i = len(path) - 1
    while i > 0:
        for j in range(len(path[i])):
            if distance(path[i][j], path[i-1][j])==2:
                print_swing(-i + len(path), path[i][j][1], path[i]
                            [j][2], path[i - 1][j][1], path[i - 1][j][2])
            else:
                print_slide(-i + len(path), path[i][j][1], path[i]
                            [j][2], path[i - 1][j][1], path[i - 1][j][2])
        i -= 1