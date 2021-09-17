# Author: Eric Vartanian
# Date: 6/8/21
# Description: Creates a class called Kuba Game where two players take turns pushing marbles on a 7x7 board.
# The first player to push off seven red marbles or push off all of the opponents marbles wins the game.
import copy


class KubaGame:
    """Represents a game where two players take turns pushing marbles on a 7x7 board. Play continues until
    seven neutral red marbles are pushed off the board or all the opposing marbles are pushed off."""
    def __init__(self, tuple1, tuple2):
        """Creates a new instance of the Kuba Game. Initializes the board to the starting position, saves
        parameters in variables, creates a player dictionary, sets the turn and winner to None, creates
        a captured marbles dictionary, and an empty list to store deep copies of the board."""
        self.board = [['W', 'W', 'X', 'X', 'X', 'B', 'B'],
                      ['W', 'W', 'X', 'R', 'X', 'B', 'B'],
                      ['X', 'X', 'R', 'R', 'R', 'X', 'X'],
                      ['X', 'R', 'R', 'R', 'R', 'R', 'X'],
                      ['X', 'X', 'R', 'R', 'R', 'X', 'X'],
                      ['B', 'B', 'X', 'R', 'X', 'W', 'W'],
                      ['B', 'B', 'X', 'X', 'X', 'W', 'W']]
        self.player_1 = tuple1
        self.player_2 = tuple2
        self.player_dict = {self.player_1[0]: self.player_1[1], self.player_2[0]: self.player_2[1]}
        self.turn = None
        self.winner = None
        self.capture_dict = {self.player_1[0]: 0, self.player_2[0]: 0}
        self.copy_list = []

    def get_winner(self):
        """Returns the winner."""
        return self.winner

    def print_board(self):
        """Prints the board."""
        for line in self.board:
            print(*line)

    def get_marble(self, coordinates):
        """Returns the marble at the specified coordinates if coordinates are in range, otherwise
        returns None."""
        if coordinates[0] not in range(7) or coordinates[1] not in range(7):
            return None
        else:
            row = coordinates[0]
            col = coordinates[1]
            return self.board[row][col]

    def get_current_turn(self):
        """Returns which players turn it currently is."""
        return self.turn

    def set_current_turn(self, player_name):
        """Sets the current turn."""
        self.turn = player_name

    def set_first_turn(self, player_name):
        """Sets the first turn."""
        if self.turn is None:
            self.set_current_turn(player_name)

    def set_next_turn(self, player_name):
        """Sets the next turn."""
        player_1 = self.player_1[0]
        player_2 = self.player_2[0]
        self.set_current_turn(player_2) if player_name == player_1 \
            else self.set_current_turn(player_1)

    def get_marble_count(self):
        """Returns the current marble count on the board in the form of a tuple (White, Black, Red)."""
        white_count = 0
        black_count = 0
        red_count = 0
        for row in range(7):
            for col in range(7):
                if self.board[row][col] == 'W':
                    white_count += 1
                elif self.board[row][col] == 'B':
                    black_count += 1
                elif self.board[row][col] == 'R':
                    red_count += 1
        return white_count, black_count, red_count

    def get_captured(self, player_name):
        """Returns the number of captured marbles for the specified player."""
        return self.capture_dict[player_name]

    def invalid_pushing_different_marble(self, player_name, coordinates):
        """Creates an invalid move scenario where the player is trying to push a marble that is not theirs
        or is trying to push a marble outside the board coordinates."""
        if self.player_dict[player_name] != self.get_marble(coordinates):
            return True
        return False

    def invalid_turn(self, player_name):
        """Creates an invalid move scenario where a player is trying to make a move when it is not their turn."""
        if player_name != self.turn:
            return True
        return False

    def invalid_pushing_with_marble_behind(self, coordinates, direction):
        """Creates an invalid move scenario where a player is trying to push a marble with a marble behind it."""
        if direction == 'F':
            f_row = coordinates[0]
            if f_row in range(6):
                f_chk_coordinates = (f_row + 1, coordinates[1])
                f_cell_behind = self.get_marble(f_chk_coordinates)
                if f_cell_behind != 'X':
                    return True
        elif direction == 'B':
            b_row = coordinates[0]
            if b_row in range(1, 7):
                b_chk_coordinates = (b_row - 1, coordinates[1])
                b_cell_behind = self.get_marble(b_chk_coordinates)
                if b_cell_behind != 'X':
                    return True
        elif direction == 'R':
            r_col = coordinates[1]
            if r_col in range(1, 7):
                r_chk_coordinates = (coordinates[0], r_col - 1)
                r_cell_behind = self.get_marble(r_chk_coordinates)
                if r_cell_behind != 'X':
                    return True
        elif direction == 'L':
            l_col = coordinates[1]
            if l_col in range(6):
                l_chk_coordinates = (coordinates[0], l_col + 1)
                l_cell_behind = self.get_marble(l_chk_coordinates)
                if l_cell_behind != 'X':
                    return True
        return False

    def invalid_move_after_win(self):
        """Creates an invalid move scenario where a player is trying to push a marble after a win."""
        if self.winner is not None:
            return True
        return False

    def invalid_ko_rule(self):
        """Creates an invalid move scenario where a player is trying to push marbles in a way that makes the board
        the same configuration as it was before the previous turn (Ko Rule)."""
        if len(self.copy_list) >= 2:
            # if marbles were pushed back to the way they were before the last move was made, reset the board
            # to the way it was before the move that caused the violation and return True
            if self.board == self.copy_list[len(self.copy_list) - 2]:
                self.board = self.copy_list[len(self.copy_list) - 1]
                return True
        return False

    def move_forward(self, player_name, coordinates):
        """Creates the forward movement and capture for the game."""
        row = coordinates[0]
        col = coordinates[1]
        row_above = row - 1
        end_row = 0
        for row_num in range(row_above, -1, -1):
            forward_check = (row_num, col)
            forward_spot = self.get_marble(forward_check)
            # if the end of the stack to be pushed is the marble on the edge of the board
            if row_num == 0:
                # if the marble at the edge of the board is the player's own marble, reject the move, return False
                if forward_spot == self.player_dict[player_name]:
                    return False
                # if the marble at the edge of the board is red, we want to add it to players captured marbles
                elif forward_spot == 'R':
                    self.capture_dict[player_name] += 1
            if forward_spot == 'X':
                end_row = row_num
                break
        # swap marble positions starting from the end of the push stack to beginning
        for spot in range(end_row, row):
            self.board[spot][col] = self.board[spot + 1][col]
        if row != 0:
            self.board[row][col] = 'X'
        # if the player is trying to push their own marble off the board
        elif row == 0:
            return False
        return True

    def move_left(self, player_name, coordinates):
        """Creates the leftward movement and capture for the game."""
        row = coordinates[0]
        col = coordinates[1]
        col_left = col - 1
        end_col = 0
        for col_num in range(col_left, -1, -1):
            left_check = (row, col_num)
            left_spot = self.get_marble(left_check)
            if col_num == 0:
                if left_spot == self.player_dict[player_name]:
                    return False
                elif left_spot == 'R':
                    self.capture_dict[player_name] += 1
            if left_spot == 'X':
                end_col = col_num
                break
        for spot in range(end_col, col):
            self.board[row][spot] = self.board[row][spot + 1]
        if col != 0:
            self.board[row][col] = 'X'
        elif col == 0:
            return False
        return True

    def move_backward(self, player_name, coordinates):
        """Creates the backward movement and capture for the game."""
        row = coordinates[0]
        col = coordinates[1]
        row_below = row + 1
        end_row = 6
        for row_num in range(row_below, 7):
            backward_check = (row_num, col)
            backward_spot = self.get_marble(backward_check)
            # if the end of the stack to be pushed is the marble on the edge of the board
            if row_num == 6:
                # if the marble at the edge of the board is the player's own marble, reject the move, return False
                if backward_spot == self.player_dict[player_name]:
                    return False
                # if the marble at the edge of the board is red, we want to add it to players captured marbles
                elif backward_spot == 'R':
                    self.capture_dict[player_name] += 1
            if backward_spot == 'X':
                end_row = row_num
                break
        # swap marble positions starting from the end of the push stack to beginning
        for spot in range(end_row, row, -1):
            self.board[spot][col] = self.board[spot - 1][col]
        if row != 6:
            self.board[row][col] = 'X'
        # if the player is trying to push their own marble off the board
        elif row == 6:
            return False
        return True

    def move_right(self, player_name, coordinates):
        """Creates the rightward movement and capture for the game."""
        row = coordinates[0]
        col = coordinates[1]
        col_right = col + 1
        end_col = 6
        for col_num in range(col_right, 7):
            right_check = (row, col_num)
            right_spot = self.get_marble(right_check)
            if col_num == 6:
                if right_spot == self.player_dict[player_name]:
                    return False
                elif right_spot == 'R':
                    self.capture_dict[player_name] += 1
            if right_spot == 'X':
                end_col = col_num
                break
        for spot in range(end_col, col, -1):
            self.board[row][spot] = self.board[row][spot - 1]
        if col != 6:
            self.board[row][col] = 'X'
        elif col == 6:
            return False
        return True

    def check_for_win(self, player_name):
        """Checks for a winning move. Returns True if move won and False otherwise."""
        # check if the player's move made the player capture 7 red marbles
        if self.capture_dict[player_name] == 7:
            self.winner = player_name
            return True
        # check if the player's move made either black or white marble count 0
        white_marbles = self.get_marble_count()[0]
        black_marbles = self.get_marble_count()[1]
        if white_marbles == 0 or black_marbles == 0:
            self.winner = player_name
            return True
        return False

    def make_move(self, player_name, coordinates, direction):
        """Makes the move for the specified player, and the specified coordinates, and in the specified direction.
        If any invalid scenarios are triggered, returns False. If the move was valid, move is made on the board
        and a copy of the board is added to a copy list. Sets turn to next player if move was valid and returns
        True."""
        # set first turn to starting player
        self.set_first_turn(player_name)
        # check for the initial invalid conditions
        if self.invalid_turn(player_name) or self.invalid_pushing_different_marble(player_name, coordinates) \
                or self.invalid_pushing_with_marble_behind(coordinates, direction) or self.invalid_move_after_win():
            return False
        # depending on the direction, make the move and check if it was valid
        elif direction == 'F':
            if self.move_forward(player_name, coordinates) is False:
                return False
        elif direction == 'B':
            if self.move_backward(player_name, coordinates) is False:
                return False
        elif direction == 'L':
            if self.move_left(player_name, coordinates) is False:
                return False
        elif direction == 'R':
            if self.move_right(player_name, coordinates) is False:
                return False
        # check if the KO rule was violated and player pushed marbles back to the previous board configuration,
        # return False if rule was violated
        if self.invalid_ko_rule():
            return False
        # check if the move was a winning move and set the winner if the move won the game and return True to end
        # the move
        if self.check_for_win(player_name):
            return True
        # if move was valid and there was no winner, make a copy of the board and store it in a list
        board_copy = copy.deepcopy(self.board)
        self.copy_list.append(board_copy)
        # set turn to other player and return True
        self.set_next_turn(player_name)
        return True
