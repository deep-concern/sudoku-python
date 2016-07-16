#!/usr/local/bin/python3

import os
import re
import sys

ILLEGAL_PATTERN = re.compile(r'(\W|\d|\s)+'g)
WORD_PATTERN = re.compile(r"([a-zA-Z])+"g)
WORDS_FILE = 'words.txt'

def main():
    # List of words for crossword puzzle
    words = []

    if os.path.isfile(WORDS_FILE): # Get words from file
        print('Parsing file...')
        with open(WORDS_FILE) as wf:
            for word in wf.readlines():
                if validate_word(word):
                    words.append(word)
        print('Parse complete')
    else: # Get words from user input
        print('Need user input...')
    print('Finished.')

    # Exit if no words
    if !(len(words) > 0):
        print('No valid words found.')
        sys.exit(1)

    word_matrix = generate_word_matrix(words)

def generate_word_matrix(words):
    return [[],]

def validate_word(word):
    # Must be a str
    if type(word) is not str:
        word = str(word)

    illegal_match = re.search(ILLEGAL_PATTERN, word)
    if illegal_match.group(0):

    m = re.match(WORD_PATTERN, word)
    if m.group

class Word(object):
    def __init__(self, id, word):
        self.word = word
        self.id = id
        self.letter_map = {}

    def is_connected(self):
        return len(self.letter_map) == True

if __name__ == '__main__':
    main()
