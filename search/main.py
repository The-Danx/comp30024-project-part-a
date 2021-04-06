"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching

This script contains the entry point to the program (the code in
`__main__.py` calls `main()`).
"""

import json
import sys
from copy import deepcopy
from search.game import remove_defeated_tokens, valid_position
from search.search import calculate_h, distance, get_g_score, Node, sort_priority_queue
from search.util import get_board_dict, print_board, print_slide, print_swing


def main():

    try:
        with open(sys.argv[1]) as file:
            data = json.load(file)
    except IndexError:
        print("usage: python3 -m search path/to/input.json", file=sys.stderr)
        sys.exit(1)

    print_board(get_board_dict(data), compact=False, ansi=True)

    # Create start and end node
    start_node = Node(None, data['upper'], data['lower'], data['block'])
    start_node.defeatedTokensRemaining = start_node

    # Initialise lists for open and closed nodes
    priority_queue = [[start_node.f, start_node]]  # [f-score, node]
    closed_list = []

    while len(priority_queue) > 0:

        priority_queue = sort_priority_queue(priority_queue)
        curr_node = priority_queue[0][1]
        if not curr_node.lower:
            # Retrace path
            path = []
            while curr_node.defeatedTokensRemaining != start_node:
                path.append(curr_node.defeatedTokensRemaining.upper)
                curr_node = curr_node.parent
            path.append(start_node.upper)
            break

        # Remove node from priority queue and add to list of visited nodes
        priority_queue.pop(0)
        closed_list.append(curr_node)

        # Do not further explore node if all upper tokens are defeated
        if not curr_node.upper:
            continue

        curr_node.get_neighbours()
        for neighbour in curr_node.neighbours:

            # Create (temporary) child node
            child_node = Node(curr_node, neighbour, list(curr_node.lower),
                              list(curr_node.block))

            # Check if the position is valid (not blocked or out of bounds)
            if not valid_position(child_node):
                continue

            child_g_score = curr_node.g + 1

            # Record g and f score and add to priority queue
            child_node.g = child_g_score
            child_node.h = calculate_h(child_node)
            child_node.f = child_node.g + child_node.h

            child_node.defeatedTokensRemaining = deepcopy(child_node)
            remove_defeated_tokens(child_node)

            if child_node in closed_list:
                # Node already visited
                continue

            if get_g_score(child_node, priority_queue) == -1:
                pass
            else:
                # Check if the child is present in the priority queue. If yes,
                # check if we will need to update the g-score.
                continue

            priority_queue.append([child_node.f, child_node])

    # Print out the final solution based upon specification
    i = len(path) - 1
    while i > 0:
        for j in range(len(path[i - 1])):
            if distance(path[i][j], path[i-1][j]) == 2:
                print_swing(-i + len(path), path[i][j][1], path[i]
                            [j][2], path[i - 1][j][1], path[i - 1][j][2])
            else:
                print_slide(-i + len(path), path[i][j][1], path[i]
                            [j][2], path[i - 1][j][1], path[i - 1][j][2])
        i -= 1
