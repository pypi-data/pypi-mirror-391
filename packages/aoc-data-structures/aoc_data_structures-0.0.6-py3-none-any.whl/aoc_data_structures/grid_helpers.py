import numpy as np


def expand_board(board, expansion_size=2):
    """
    Expand a 2-d numpy array by duplicating elements.

    Example expand by 2:

        original:
            1 0
            0 1

        expanded:
            1 1 0 0
            1 1 0 0
            0 0 1 1
            0 0 1 1
    """
    board = np.repeat(board, expansion_size, axis=0)
    return np.repeat(board, expansion_size, axis=1)


def parse(lines):
    board = []

    for line in lines:
        board.append(list(line.strip()))

    return np.array(board)


def board_str(board):
    """
    Return the string representation of a numpy array where each element can be
    represented as a single character.
    """
    return "\n".join("".join(row) for row in board)


def hash_array(array):
    return hash("".join(array.flatten()))
