import numpy as np
from typing import List, Tuple, Optional
from copy import deepcopy


class CheckersGame:
    """
    A class representing a game of Checkers.

    Attributes:
        - board (np.ndarray): An 8x8 numpy array representing the board state.
        - current_player (int): The current player (1 for black, -1 for white).

    Methods:
        - get_valid_moves() -> List[Tuple[Tuple[int, int], List[Tuple[int, int]]]]: Returns a list of valid moves.
        - make_move(start_pos: Tuple[int, int], moves: List[Tuple[int, int]]) -> None: Executes a move or a sequence of captures.
        - is_game_over() -> bool: Determines if the game is over.
        - get_winner() -> Optional[int]: Returns the winner (-1 for white, 1 for black, None if game is ongoing).
        - get_state() -> np.ndarray: Returns a deep copy of the board state.
    """

    # Board representation:
    # 0 = empty
    # 1 = black piece
    # 2 = black king
    # 3 = white piece
    # 4 = white king

    board: np.ndarray
    current_player: int

    def __init__(self):
        self.board = np.zeros((8, 8), dtype=int)
        self.current_player = 1  # 1 for black, -1 for white

        self._initialize_board()

    def _initialize_board(self):
        """Initializes 8x8 board"""

        # Set up black pieces (top of board)
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    self.board[row][col] = 1

        # Set up white pieces (bottom of board)
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    self.board[row][col] = 3

    def get_valid_moves(self) -> List[Tuple[Tuple[int, int], List[Tuple[int, int]]]]:
        """Returns list of valid moves in format (start_pos, [capture_positions])"""
        moves = []
        capture_moves = []  # Jumps are mandatory

        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                # Check if piece belongs to current player
                if self._is_current_players_piece(piece):
                    piece_captures = self._get_capture_moves(
                        row, col)  # Check for possible captures
                    if piece_captures:
                        capture_moves.extend(((row, col), captures)
                                             for captures in piece_captures)
                    else:
                        piece_moves = self._get_normal_moves(row, col)
                        moves.extend(((row, col), [move])
                                     for move in piece_moves)

        return capture_moves if capture_moves else moves

    def _is_current_players_piece(self, piece: int) -> bool:
        if self.current_player == 1:  # Black's turn
            return piece in [1, 2]  # Black piece or king
        else:  # White's turn
            return piece in [3, 4]  # White piece or king

    def _get_normal_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Finds all pieces belonging to self.current_player and returns list of all possible non-capture moves"""
        moves = []
        piece = self.board[row][col]

        directions = []
        if piece in [1, 2]:  # Black piece or king
            directions.extend([(1, -1), (1, 1)])
        if piece in [3, 4]:  # White piece or king
            directions.extend([(-1, -1), (-1, 1)])
        if piece in [2, 4]:  # Kings can move backwards
            directions.extend([(-1, -1), (-1, 1)] if piece ==
                              2 else [(1, -1), (1, 1)])

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self._is_valid_position(new_row, new_col) and self.board[new_row][new_col] == 0:
                moves.append((new_row, new_col))

        return moves

    def _get_capture_moves(self, row: int, col: int) -> List[List[Tuple[int, int]]]:
        captures = []
        self._find_capture_sequences(row, col, [], captures, set())
        return captures

    def _find_capture_sequences(self, row: int, col: int, current_sequence: List[Tuple[int, int]],
                                all_sequences: List[List[Tuple[int, int]]], visited: set) -> None:
        """Takes in the current position and sequence of jumps and finds all possible capture sequences. Used recursively, directly appends to sequences instead of returning anything."""

        piece = self.board[row][col]

        directions = []
        if piece in [2, 4]:  # Kings
            directions.extend([(2, -2), (2, 2), (-2, -2), (-2, 2)])
        elif piece == 1:  # Black piece
            # Bottom left, bottom right respectively
            directions.extend([(2, -2), (2, 2)])
        elif piece == 3:  # White piece
            # Top left, top right respectively
            directions.extend([(-2, -2), (-2, 2)])

        found_capture = False
        for dx, dy in directions:
            new_row, new_col = row + dx, col + dy  # End position after jump
            jumped_row, jumped_col = row + dx//2, col + dy//2  # Position jumped over

            if ((new_row, new_col) not in visited and
                # Check if new position is on board
                self._is_valid_position(new_row, new_col) and
                # Check if new position is empty
                self.board[new_row][new_col] == 0 and
                    self._is_opponent_piece(self.board[jumped_row][jumped_col])):  # Check if jumping over opponent's piece

                found_capture = True
                visited.add((new_row, new_col))
                new_sequence = current_sequence + \
                    [(new_row, new_col)]  # Add jump to sequence
                self._find_capture_sequences(
                    new_row, new_col, new_sequence, all_sequences, visited)
                visited.remove((new_row, new_col))

        if not found_capture and current_sequence:
            all_sequences.append(current_sequence)

    def _is_opponent_piece(self, piece: int) -> bool:
        if self.current_player == 1:  # Black's turn
            return piece in [3, 4]  # White pieces
        else:  # White's turn
            return piece in [1, 2]  # Black pieces

    def _is_valid_position(self, row: int, col: int) -> bool:
        return 0 <= row < 8 and 0 <= col < 8

    def make_move(self, start_pos: Tuple[int, int], moves: List[Tuple[int, int]]) -> None:
        """Make a move or sequence of captures"""
        row, col = start_pos
        piece = self.board[row][col]

        # Move the piece through the sequence
        self.board[row][col] = 0
        for i, (new_row, new_col) in enumerate(moves):

            # CAPTURE
            if abs(new_row - row) == 2:
                jumped_row = (new_row + row) // 2
                jumped_col = (new_col + col) // 2
                self.board[jumped_row][jumped_col] = 0

            # LAST MOVE
            if i == len(moves) - 1:  # Final position
                # Check if piece should be kinged
                if piece == 1 and new_row == 7:  # Black piece reaches bottom
                    piece = 2
                elif piece == 3 and new_row == 0:  # White piece reaches top
                    piece = 4
                self.board[new_row][new_col] = piece
            row, col = new_row, new_col

        self.current_player *= -1  # Switch players

    def is_game_over(self) -> bool:
        return len(self.get_valid_moves()) == 0

    def get_winner(self) -> Optional[int]:
        if not self.is_game_over():
            return None
        return -self.current_player  # Previous player won

    def get_state(self) -> np.ndarray:
        return self.board.deepcopy()

    def __str__(self) -> str:
        symbols = {0: ".", 1: "b", 2: "B", 3: "w", 4: "W"}
        board_str = "  0 1 2 3 4 5 6 7\n"
        for i in range(8):
            board_str += f"{i} "
            for j in range(8):
                board_str += symbols[self.board[i][j]] + " "
            board_str += "\n"
        return board_str
