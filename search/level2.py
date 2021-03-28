"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching

This script contains the entry point to the program (the code in
`__main__.py` calls `main()`). Your solution starts here!
"""

import sys
import json
from copy import deepcopy


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
        self.g = 0 # Distance so far
        self.h = 0 # Distance to goal
        self.f = 0 # Total distance from start to goal


def valid_position(node):
    """valid_position returns true if the position is not blocked by a block token or 
    is inside the board"""
    
    ran = range(-4, +4+1)
    valids =  [rq for rq in [(r,q) for r in ran for q in ran if -r-q in ran]]
    blocks = [(i[1],i[2]) for i in node.block]
    valids = [pos for pos in valids if pos not in blocks]

    tok = (node.upper[0][1], node.upper[0][2])
    
    if tok in valids:
        return 1
    return 0

def token_defeated(node):
    """returns the indices of the lower tokens defeated, if none return -1 """
    
    up = node.upper[0]

    indices = [] # indices of lower tokens that share the same hex as up
    for i, lo in enumerate(node.lower):
        if (up[1], up[2]) == (lo[1], lo[2]):
            u = up[0]
            l = lo[0]

            if ((u == 'r' and l =='s') or 
            (u == 'p' and l =='r') or 
            (u == 's' and l =='p')):
                return i
    return -1

def sign(num):
    # sign function
    if num<0: 
        return -1
    else:
        return 1

def simple_h(up, lo):
    # calculate the estimated cost to reach from up to lo
    
    dr = up[1] - lo[1]
    dq = up[2] - lo[2]

    if sign(dr) == sign(dq):
        return abs(dr+dq)
    else:
        return max(abs(dr), abs(dq))

def distance(node):
    """calculate the estimated cost (h) for a node to reach its goal state. 
    If there are multiple lower tokens, calculate the distance to the closest
    winning token, and then distance from that winning token to the next 
    closest winning token, etc. For example R -> s1 -> s2 """
    
    up = node.upper[0]
    total_h = 0
    lower_toks = list(node.lower) #create copy 

    while len(lower_toks):
        h = [] 
        for lo in lower_toks:
            h.append(simple_h(up, lo))
        i = h.index(min(h))
        total_h += h[i]
        up = lower_toks.pop(i)
        
    return sum(h)

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
    checks if the combination of upper tokens and lower tokens can be found in the 
    priority queue; and if yes, returns the g-score of the similar node found
    in the priority queue. It returns -1 if it is not present """
    nodes = [(n.upper,n.lower) for f,n in pq]

    try:
        # find index i of the corresponding node, will raise an error if not found
        i = nodes.index((node.upper, node.lower))
        # return the g-score of the i'th node in priority queue 
        return [n.g for f,n in pq][i]
    except:
        return -1

def sort_priority_queue(pq):
    """sorts the priority queue by f-score. Also puts node that have the least number of 
    lower tokens at the front. This ensures that the algorithm looks at states that are closer
    to the goal first"""

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
    
    # print(data)
    print_board(get_board_dict(data), compact=False)
    
    # Create start and end node
    start_node = Node(None, data['upper'], data['lower'], data['block'])

    # Initialise lists for open and closed nodes
    priority_queue = [[start_node.f, start_node]]  # [f-score, node]
    closed_list = []

    new_positions = [(1,0), (0,1), (-1,1), (-1,0), (0,-1), (1,-1)]

    while len(priority_queue) > 0:
    # for i in range(3):

        priority_queue = sort_priority_queue(priority_queue)
        curr_node = priority_queue[0][1]
        
        # print("OPEN LIST:")
        # print_priority_queue(priority_queue)
        # print("current node\t", curr_node.upper)
        # print_board(get_board_dict(curr_node))  
        
        if not curr_node.lower:
            # Goal state reached (no lower tokens left)
            print("Goal reached!")

            # print("\nCLOSED LIST:", closed_list, "\n")
            print("Number of steps required: ", curr_node.f)
            # print("PRIORITY QUEUE: ", priority_queue)
            # print_priority_queue(priority_queue)

            # retrace path 
            path = []
            while curr_node != start_node:
                path.append(curr_node.upper[0])
                curr_node = curr_node.parent
            break

        # Remove node from priority queue and add to list of visited nodes
        priority_queue.pop(0) 
        closed_list.append(curr_node)

        # Generate children (when there's one upper token only)
        for direction in new_positions:

            neighbour = list(curr_node.upper[0])  # create copy of list so as not to affect original node
            neighbour[1] = neighbour[1] + direction[0]
            neighbour[2] = neighbour[2] + direction[1]
            # print("neighbour: ", neighbour)
                        
            # Create (temporary) child node
            child_node = Node(curr_node, [neighbour], list(curr_node.lower), list(curr_node.block))
            
            # check if the position is valid (not blocked or out of bounds)
            if not valid_position(child_node):
                continue
            
            
            child_g_score = curr_node.g + 1

            if child_node in closed_list:
                # Node already visited
                continue 

            if get_g_score(child_node, priority_queue) == -1:
                pass
            else:
                # Check if the child is present in the priority queue. If yes,
                # check if we will need to update the g-score
                continue


            # Record g and f score and add to priority queue
            child_node.g = child_g_score
            child_node.h = distance(child_node)
            child_node.f = child_node.g + child_node.h

            index = token_defeated(child_node) 
            if index == -1:
                # no token was defeated
                pass
            else:
                # Remove defeated token from board
                child_node.lower.pop(index)  
            
            # print_node(child_node)

            priority_queue.append([child_node.f, child_node])
            # print("\n")
            
            
        
        # print("\n")

    print(path[::-1])
            
            
def print_priority_queue(pq):
    for i,j in pq:
        print("PRIORITY QUEUE", (i,j.upper, j.lower))

def print_node(node):
    print("upper:", node.upper)
    print("lower:", node.lower)
    print("f:", node.f)