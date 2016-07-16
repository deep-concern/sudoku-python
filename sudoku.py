#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""A collection of functions for generating and solving sudoku puzzles."""

import logging
import os
import random
import re
import sys

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

class SudokuGrid(object):
    """Class to hold information about a sudoku."""
    def __init__(self, sudoku_string):
        self.sudoku_string = sudoku_string
        self.grid = parse_sudoku_string(sudoku_string)

class RetryError(Exception):
    """Exception for when a function fails to produce a result after a limit."""
    def __init__(self, retry_number = None, retry_limit = None):
        if retry_number is not None and type(retry_number) is not int:
            raise TypeError("Parameter `retry_number` is not of type int")
        if retry_limit is not None and type(retry_limit) is not int:
            raise TypeError("Parameter `retry_number` is not of type int")
        self.retry_number = retry_limit
        self.retry_limit = retry_limit
    def __str__(self):
        retry_limit_text = ""
        retry_number_text = ""
        if self.retry_limit is not None:
            retry_limit_text = "(" + str(self.retry_limit) + ")"
        if self.retry_number is not None:
            retry_number_text = "(" + str(self.retry_number) + ")"
        return "Current retry number{0} surpassed retry limit ({1})".format(retry_number_text, retry_limit_text)

def is_proper_sudoku(sudoku_string):
    """Uses a regex expression to validate a sudoku string.

    Sudoku strings need to be 81 characters using digits 0-9, or '.'

    Args(str): A string to be validated.

    Returns:
        bool: True if the string is a proper sudoku string. False otherwise.
    """
    # Must be type 'str'
    if type(sudoku_string) != str:
        return False

    # Sudokus should only have 81 squares (currently)
    if len(sudoku_string) != 81:
        return False

    #
    m = re.search(r"[0-9/.]{81}]", sudoku_string)
    return m is not None




def parse_sudoku_string(sudoku_string):
    """Parses a sudoku saved as a string into a grid to be parsed.

    Takes a string of given values, with '0' or '.' being empty spaces, and
    attempts to create a dictionary of given values.

    No attempts will be made to verify

    Args:
        sudoku_string(str): A string of length 81 that contains either digits
            from 0-9, or '.'.

            The string is parsed left to right, filling out grid from left to
            right, top to bottom.

            Digits 1-9 will be considered as given values, and '0' or '.' will
            be blanks.

    Returns:
        dict: A dictionary where the keys are 2D coordinates of given values
        and the values will be a digit from 1 to 9.

        This can be used as givens for a sudoku, or if the dict contains 81
        keys, this may be a solution.


    """
    if not is_proper_sudoku(sudoku_string):
        return False

    grid = {}

    for y in range(9):
        offset = y * 8
        for x in range(9):
            index = offset + x
            if not check_valid_space(x, y, sudoku_string[index], grid):
                return False
            else:
                grid



def print_board(board):
    """Prints out the contents of a dict mapped to a sudoku puzzle.

    This function assumes that `board` is a dictionary containing key, value
    pairs where the key is a coordinate within the sudoku board and value is a
    value from 1 to 9.

    """
    # Requires a dict
    if type(board) is not dict:
        raise TypeError("Requires 'dict' instance")

    # Loop through the board, printing a each value within a grid
    for j in range(9):
        if  j == 3 or j == 6:
            # Block seperator
            print("-----------")
        num_list = []
        # Values of current row
        for i in range(9):
            if (i,j) not in board:
                num_list.append(".")
            else:
                num_list.append(board[(i,j)])

        print("{0}{1}{2}|{3}{4}{5}|{6}{7}{8}".format(num_list[0],
                num_list[1], num_list[2], num_list[3], num_list[4], num_list[5],
                num_list[6], num_list[7], num_list[8]))

def generate_givens(number_of_givens, retry_limit = 1000):
    """Generates a sudoku board with randomly generated givens."""
    if number_of_givens > 81 or number_of_givens < 0:
        raise ValueError("Number of givens must be from 0 to 81")

    # Board to hold our givens
    board = {}

    # Retry counter
    retry = 0

    # Keep going until we have the desired amount
    while len(board) != number_of_givens:
        # Check to see if we surpassed our retry limit
        if retry > retry_limit:
            raise RetryError(retry_number=retry, retry_limit=retry_limit)

        # Create a random position and value
        attempt_x = random.randint(0,8)
        attempt_y = random.randint(0,8)
        attempt_value = random.randint(1, 9)

        # Check if position already taken
        if not check_valid_space(attempt_x, attempt_y, attempt_value, board):
            # Try again with another valid value and position
            retry += 1
            continue

        # Add value to board
        board[(attempt_x,attempt_y)] = attempt_value

    return board


def depth_first_solve(givens = {}):
    """ Tries to solve a sudoku using depth-first algorithm."""

    # A dict of currently available values (should be nine each)
    available_values = {x:9 for x in range(1,10)}

    # Dict of (x,y) keys to hold current solution - add current givens
    board = dict(givens)

    # Remove given values from available values
    for (given_x, given_y) in givens:
        available_values[givens[(given_x, given_y)]] -= 1

    # Solver helper
    def solve_help(current_board, available_values, solutions = set(), retry = 0):
        """Helper function for depth-first algorithm."""
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

                solutions_set = solve_help(new_board, new_values, solutions, retry + 1)

                # Add new solutions to current solutions
                for solution in solutions_set:
                    solutions.add(solution)

        # Return solutions acquired
        return solutions

    # Solve
    return solve_help(board, available_values)


def find_available_space(board):
    """Traverses the sudoku board finding the first available space.

    This function assumes that `board` is a dictionary containing key, value
    pairs where the key is a coordinate within the sudoku board and value is a
    value from 1 to 9.
    """
    for y in range(9):
        for x in range(9):
            if (x,y) not in board:
                return (x,y)

def check_valid_space(x, y, val, board):
    """ Checks if the value fits in the sudoku board following standard rules.

    This function assumes that `board` is a dictionary containing key, value
    pairs where the key is a coordinate within the sudoku board and value is a
    value from 1 to 9.

    """
    # Check row if number is already placed
    for i in range(9):
        # Is valid position and value is equal to what we want to add
        if (i, y) in board and board[(i, y)] == val and (i, y) != (x,y):
            return False

    # Check column
    for i in range(9):
        # Is valid position and value is equal to what we want to add
        if (x, i) in board and board[(x,i)] == val and (x, i) != (x,y):
            return False

    # Check box
    box_x = x//3 * 3
    box_y = y//3 * 3
    for j in range(3):
        for i in range(3):
            # Is valid position and value is equal to what we want to add
            if (i + box_x, j + box_y) in board and board[(i + box_x, j + box_y)] == val and (i + box_x, j + box_y) != (x,y):
                return False

    return True

def generate_sudoku(number_of_givens, retry_limit=10000):
    """Attempts to generate a valid sudoku with a certain amount of givens."""
    # Bool to hold whether or the puzzle can be solved and if it only has one solution
    is_proper_sudoku = False

    # Set a retry limit
    retry = 0

    # Givens and solution set with solution to return
    givens = {}
    solutions = set()

    while not is_proper_sudoku:
        # Generate givens
        givens = generate_givens(number_of_givens)
        givens = {}

        # Get solutions
        solutions = depth_first_solve(givens)

        is_proper_sudoku = len(solutions) == 1

        if not is_proper_sudoku:
            retry += 1
            print("Retrying... {0}".format(retry))
            continue
        if retry >= retry_limit:
            raise RetryError(retry_number=retry, retry_limit=retry_limit)

    return givens, solutions.pop()


def main():
    """Main function that generates and solves a sudoku."""
    print("Generating given values...")

    # Board containing initially given values and positions
    test_givens = ''

    # Get a valid sudoku
    givens, solution = generate_sudoku(11)

    print("Initial grid:")
    print_board(givens)

    print("Solved grid(s):")
    print_board(dict(solution))


if __name__ == '__main__':
    main()

## References
# http://norvig.com/sudoku.html
