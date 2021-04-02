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

WIN = 'w'
LOSE = 'l'
DRAW = 'd'

# If you want to separate your code into separate files, put them
# inside the `search` directory (like this one and `util.py`) and
# then import from them like this:
from search.util import print_board, print_slide, print_swing

class Node():

    def __init__(self, parent=None, upper=None, lower=None, block=None):

        self.parent = parent
        self.upper = upper
        self.lower = lower # Axial coordinates (r,q)
        self.block = block
        self.neighbours = []
        self.g = 0 # Distance so far
        self.h = 0 # Distance to goal
        self.f = 0 # Total distance to goal from start

    def get_neighbours(self):
        """Get all combinations of neighbours of the upper tokens"""
        new_positions = [(1,0), (0,1), (-1,1), (-1,0), (0,-1), (1,-1)]
        n = len(self.upper)
        self.neighbours = []
        swing_dic = defaultdict(set)
        for combination in product(new_positions, repeat=n):
            neighbour = deepcopy(self.upper)
            for i in range(n):
                # slide actions
                neighbour[i][1] = neighbour[i][1] + combination[i][0]
                neighbour[i][2] = neighbour[i][2] + combination[i][1]

            # print(neighbour)
            self.neighbours.append(neighbour)

            # swing actions
            before = list(self.upper)
            for i, new_up in enumerate(neighbour):
                for old_up in before:
                    if (new_up[1], new_up[2]) == (old_up[1], old_up[2]):
                        # new_up can swing around old_up
                        
                        count = 0 
                        for direction in new_positions:
                            possible_swing = list(new_up) 
                            possible_swing[1] = possible_swing[1] + direction[0]
                            possible_swing[2] = possible_swing[2] + direction[1]

                            if simple_h(possible_swing, before[i]) == 2:
                                valid_swing = list(neighbour)
                                valid_swing[i] = possible_swing
                                swing_dic[i].add(tuple(possible_swing))                            
                                count += 1
                                
                                self.neighbours.append(valid_swing)
                                # print("possible_swing: ", possible_swing)
      
                            # stop when we already found the 3 swing positions
                            if count == 3:
                                break
            
        # more combinations of swings
        # print(swing_dic)
        for i in list(product(swing_dic[0], swing_dic[1])):
            self.neighbours.append(i)



        return self.neighbours


def valid_position(node):
    """valid_position returns true if the position is not blocked by a block 
    token and is inside range of the board"""
    
    ran = range(-4, +4+1)
    valids =  [rq for rq in [(r,q) for r in ran for q in ran if -r-q in ran]]
    blocks = [(i[1],i[2]) for i in node.block]
    valids = [pos for pos in valids if pos not in blocks]

    for up in node.upper:
        tok = (up[1], up[2])
        if tok not in valids:
            return 0
    return 1

def battle(u, l):
    """ return WIN if tok1 defeats tok2, 
               DRAW if tok2 is defeated by tok2
               DRAW if none is defeated """  
    if ((u == 'r' and l =='s') or 
        (u == 'p' and l =='r') or 
        (u == 's' and l =='p')):
        return WIN 
    elif ((u == 's' and l =='r') or 
         (u == 'r' and l =='p') or 
         (u == 'p' and l =='s')):
        return LOSE
    else: 
        return DRAW

def upper_wl_upper(which, up_vs_lo, i):
    """Return the list of indices of upper and lower tokens to be removed when 
       up1 wins or loses with up2. Parameter "which" is the index of upper 
       token which won up_vs_up"""

    if up_vs_lo == WIN:
        # lower token has same symbol as u2
        return [[int(not which)],[i]] # other upper token and lower token defeated
    elif up_vs_lo == LOSE:
        # up1, up2, and lower token all have different symbols
        return [[0,1], [i]] # all tokens defeated
    elif up_vs_lo == DRAW:
        # only u2 is defeated
        return [[int(not which)], []]

def upper_d_upper(up_vs_lo, i):
    """Return the list of indices of upper and lower tokens to be removed when
       up1 draws with up2"""
    if up_vs_lo == WIN:
        return [[], [i]] # lower token is defeated
    elif up_vs_lo == LOSE:
        return [[0,1], []] # both upper tokens are defeated
    elif up_vs_lo == DRAW:
        return [[], []] # nothing happens

def upper_vs_lower(which, u, l, tokens_defeated, i):

    up_vs_lo = battle(u, l)
    if up_vs_lo == WIN:
        tokens_defeated[1].append(i)
    elif up_vs_lo == LOSE:
        tokens_defeated[0].append(int(not which))

    return tokens_defeated

def find_defeated_tokens(node):
    """Return a list that contains the indices of the upper and lower 
    tokens to be removed"""
    
    tokens_defeated = [[],[]]

    if len(node.upper) == 1:
        up = node.upper[0]
        # Find the index of the lower token defeated
        for i, lo in enumerate(node.lower):
            if (up[1], up[2]) == (lo[1], lo[2]):
                # The upper token always defeats the lower token
                # at this point anyway, since game specifications
                # says the game will always be winnable
                return [[],[i]]
        return tokens_defeated # will be empty list
    
    elif len(node.upper) == 2:
        up1 = node.upper[0]
        up2 = node.upper[1]
        for i, lo in enumerate(node.lower):

            # if both upper tokens share the same hex as lower token
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

def sign(num):
    # sign function
    if num<0: 
        return -1
    else:
        return 1

def simple_h(tok1, tok2):
    # calculate the estimated cost to reach from tok1 to tok2
    dr = tok1[1] - tok2[1]
    dq = tok1[2] - tok2[2]

    if sign(dr) == sign(dq):
        return abs(dr+dq)
    else:
        return max(abs(dr), abs(dq)) 

def winning_symbol(up):
    # winning_symbol returns the symbol that is defeated by up
    if up=="r":
        return "s"
    elif up=="s":
        return "p"
    elif up=="p":
        return "r"

def distance(node):
    """calculate the estimated cost (h) for a node to reach its goal state. 
    If there are multiple lower tokens, calculate the distance to the closest
    winning token, and then distance from that winning token to another winning 
    token. In other words, for example R -> s1 -> s2 """
    
    total_h = 0
    # print("PARENT: upper: ", node.parent.upper, "\tlower: ", node.parent.lower)
    # print("CURRENT: upper: ", node.upper, "\tlower: ", node.lower)
    for up in node.upper:
        # print("current upper: ", up)
        lower_toks = list(node.lower)
        upper_symbol = up[0]
        while len(lower_toks):
            h = []
            for lo in lower_toks:
                # make sure we are only considering the "goal" lower tokens
                # with respect to the upper token 
                if winning_symbol(upper_symbol) == lo[0]:
                    h.append(simple_h(up, lo))
                else:
                    h.append(float('inf')) # infinite distance
            # print("h:", h)
            if all(x==float('inf') for x in h) and len(h)==len(lower_toks):
                # means the upper token does not have any goal. In this case
                # its h value is 0 
                break
            else:
                i = h.index(min(h))
                total_h += h[i]
                up = lower_toks.pop(i)
        
        # print("total_h:", total_h)
    # print("\n")
    
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
    nodes = [(n.upper,n.lower) for f,n in pq]

    try:
        # find index i of the corresponding node, raise error if not found
        i = nodes.index((node.upper, node.lower))
        # return the g-score of the i'th node in priority queue 
        return [n.g for f,n in pq][i]
    except:
        return -1

def sort_priority_queue(pq):
    """sorts the priority queue by f-score. Also puts node that have the 
    least number of lower tokens at the front. This ensures that the 
    algorithm looks at states that are closer to the goal first"""

    pq = sorted(pq, key=lambda x: x[0])
    min_f = pq[0][0] # least f-score
    min_count = len(pq[0][1].lower) # least number of lower tokens
    best_i = 0 # index of best node

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

    # count = 0
    while len(priority_queue) > 0:
    # for i in range(2):

        priority_queue = sort_priority_queue(priority_queue)
        curr_node = priority_queue[0][1]

        # print("==================================")        
        # print("OPEN LIST:")
        # print_priority_queue(priority_queue)
        # print("current node\t", curr_node.upper)
        # print_board(get_board_dict(curr_node))  

        if not curr_node.lower:
            # Goal state reached (no lower tokens left)
            # print("Goal reached!")

            # print("\nCLOSED LIST:", closed_list, "\n")
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
            child_node.h = distance(child_node)
            child_node.f = child_node.g + child_node.h

            indices = find_defeated_tokens(child_node) 
            # upper tokens to be removed

            for u in indices[0][::-1]:
                child_node.upper.pop(u)
            # lower tokens to be removed
            for l in indices[1][::-1]:
                child_node.lower.pop(l)

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
        
        # count+= 1
        # print("=========================================================")
    # print(count)
    # print("\n")
    for i in path[::-1]:
        print(i)

    # i = len(path) - 1
    # while i > 0:
    #     print_move(path, i)
    #     i -= 1
            
def print_priority_queue(pq):
    print(pq[0][0], pq[0][1].upper, pq[0][1].lower)
    # for i,j in pq:
        # print("PRIORITY QUEUE", (j.g, j.h, j.f, j.upper, j.lower))

def print_move(path, turn):
    # print(path)
    print("Turn %d: SLIDE from (%d,%d) to (%d,%d)" % (-turn + len(path), \
            path[turn][0][1], path[turn][0][2], path[turn - 1][0][1], 
            path[turn - 1][0][2]))