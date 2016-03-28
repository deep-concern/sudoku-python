#!/usr/local/bin/python3

import logging
import os
import random
import re
import sys

from collections import OrderedDict

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

class Grid(object):

    def __init__(self, number_of_givens=50):

        # The value of 'number_of_givens' must be positive and greater than 0
        if number_of_givens < 1:
            raise ValueError("number_of_givens must be positive and greater than 0")

        # Grid containing initially given values and positions
        self.given_grid = {
                                                                                                (7,0): 7,
                                                            (4,1): 8,   (5,1): 6,   (6,1): 2,
                                                (3,2): 2,   (4,2): 3,               (6,2): 4,
                                    (2,3): 4,                                                   (7,3): 2,
                        (1,4): 1,   (2,4): 3,                           (5,4): 4,
                        (1,5): 7,                           (4,5): 1,   (5,5): 5,                           (8,5): 4,
                        (1,6): 3,   (2,6): 1,                                                   (7,6): 4,   (8,6): 2,
            (0,7): 6,                           (3,7): 7,                           (6,7): 3,   (7,7): 8,
                                                                        (5,8): 1,   (6,8): 6


        }
        prev_grid = {
                        (1,0): 7,                                       (5,0): 6,
            (0,1): 9,                                                                           (7,1): 4,   (8,1): 1,
                                    (2,2): 8,                           (5,2): 9,               (7,2): 5,
                        (1,3): 9,                                       (5,3): 7,                           (8,3): 2,
                                    (2,4): 3,                                       (6,4): 8,
            (0,5): 4,                           (3,5): 8,                                       (7,5): 1,
                        (1,6): 8,               (3,6): 3,                           (6,6): 9,
            (0,7): 1,   (1,7): 6,                                                                           (8,7): 7,
                                                                        (5,8): 5,               (7,8): 8,
        }

        # Grid containing solution to the puzzle
        self.solutions = {}

        # Whether or the puzzle can be solved
        self.is_solvable = False

        # Keep generating new puzzles until we find one that is solvable
        retry = 0
        retry_limit = 100000
        while not self.is_solvable:
            #self.__generate_givens(number_of_givens)
            self.solutions = depth_first_solve(self.given_grid)

            self.is_solvable = len(self.solutions) != 0

            if not self.is_solvable:
                retry += 1
                logger.debug("Retrying... Count:{0}".format(retry))
            if retry >= retry_limit:
                logger.warning("Solve failure")
                break

    def __generate_givens(self, number_of_givens):
        # Keep going until we have the desired amount
        while len(self.given_grid) != number_of_givens:
            # Create a random position and value
            pos = (random.randint(0,8), random.randint(0,8))
            val = random.randint(1, 9)

            # Check if position already taken
            if pos in self.given_grid:
                continue

            # Attempt to add value
            self.__attempt_add(self.given_grid, pos, val)

def print_grid(grid, log=False):
    # Requires 'Grid' instance
    if type(grid) is not dict:
        raise ValueError("Requires 'dict' instance")

    # Loop through grid, printing box
    for j in range(9):
        if j == 0:
            # Top border
            print("-------------------")
        elif j == 3 or j == 6:
            # Block seperator
            print("|█████████████████|")
        else:
            print("------█-----█------")
        num_list = []
        # Values of current row
        for i in range(9):
            if (i,j) not in grid:
                num_list.append(" ")
            else:
                num_list.append(grid[(i,j)])
        if not log:
            print("|{0}|{1}|{2}█{3}|{4}|{5}█{6}|{7}|{8}|".format(num_list[0],
                    num_list[1], num_list[2], num_list[3], num_list[4], num_list[5],
                    num_list[6], num_list[7], num_list[8]))
        else:
            logger.debug("|{0}|{1}|{2}█{3}|{4}|{5}█{6}|{7}|{8}|".format(num_list[0],
                    num_list[1], num_list[2], num_list[3], num_list[4], num_list[5],
                    num_list[6], num_list[7], num_list[8]))


    # Bottom border
    print("-------------------")

def main():
    print("Creating sudoku...")
    puzzle = Grid(number_of_givens=11)
    print("Initial grid:")
    print_grid(puzzle.given_grid)

    if puzzle.is_solvable:
        print("Solved grid(s):")
        for grid in puzzle.solutions:
            print_grid(dict(grid))
    else:
        logger.warning("Could not create solvable puzzle")


def depth_first_solve(givens = {}):
    decision_tree = {}

    # A dict of currently available values (should be nine each)
    available_values = {x:9 for x in range(1,10)}

    # Dict of (x,y) keys to hold current solution - add current givens
    board = dict(givens)

    # Remove given values from available values
    for (given_x, given_y) in givens:
        available_values[givens[(given_x, given_y)]] -= 1

    # Solver helper
    def solve_help(current_board, available_values, solutions = set()):
        # Check if solved
        values_left = 0

        for i in range(1,10):
            values_left += available_values[i]

        if values_left == 0:
            # Return solution
            solutions.add(frozenset(current_board.items()))
            return solutions

        # Find the next available space
        x,y = find_available_space(current_board)

        # Go through available values and try to find a match
        for value, quantity in available_values.items():
            # Skip to the next one if empty
            if quantity == 0:
                continue

            # Check if value fits in the boards according to the rules
            if check_valid_space(x, y, value, current_board):
                # Copy available values and try solving with this value
                new_values = dict(available_values)
                new_board = dict(current_board)

                new_values[value] -= 1
                new_board[(x,y)] = value

                solutions_set = solve_help(new_board, new_values, solutions)

                # Add new solutions to current solutions
                for solution in solutions_set:
                    solutions.add(solution)

        # Return solutions acquired
        return solutions

    # Solve
    return solve_help(board, available_values)


def find_available_space(current_board):
    for y in range(9):
        for x in range(9):
            if (x,y) not in current_board:
                return (x,y)

def check_valid_space(x, y, val, current_board):

        # Check row if number is already placed
        for i in range(9):
            # Is valid position and value is equal to what we want to add
            if (i, y) in current_board and current_board[(i, y)] == val and (i, y) != (x,y):
                return False

        # Check column
        for i in range(9):
            # Is valid position and value is equal to what we want to add
            if (x, i) in current_board and current_board[(x,i)] == val and (x, i) != (x,y):
                return False

        # Check box
        box_x = x//3 * 3
        box_y = y//3 * 3
        for j in range(3):
            for i in range(3):
                # Is valid position and value is equal to what we want to add
                if (i + box_x, j + box_y) in current_board and current_board[(i + box_x, j + box_y)] == val and (i + box_x, j + box_y) != (x,y):
                    return False

        return True



if __name__ == '__main__':
    main()
