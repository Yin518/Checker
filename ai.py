from board import Board
from copy import deepcopy
from random import choice

class AI:
	def __init__(self, color):
		# 'color' is the color this AI will play with (B or W)
		self.color = color
	

	def minimax(self, current_board, is_maximizing, depth, turn):
		# Tries to find recursively the best value depending on which player is passed as an argument to the function
		if depth == 0 or current_board.get_winner() is not None:
			return self.get_value(current_board)
		
		next_turn = 'B' if turn == 'W' else 'W'
		board_color_up = current_board.get_color_up()
		current_pieces = current_board.get_pieces()
		piece_moves = list(map(lambda piece: piece.get_moves(current_board) if piece.get_color() == turn else False, current_pieces))

		if is_maximizing:
			# A max player will attempt to get the highest value possible.
			maximum = -999
			for index, moves in enumerate(piece_moves):
				if moves == False:
					continue

				for move in moves:
					aux_board = Board(deepcopy(current_pieces), board_color_up)
					aux_board.move_piece(index, int(move["position"]))
					maximum = max(self.minimax(aux_board, False, depth - 1, next_turn), maximum)
				
			return maximum
		else:
			# A min player will attempt to get the lowest value possible.
			minimum = 999
			for index, moves in enumerate(piece_moves):
				if moves == False:
					continue

				for move in moves:
					aux_board = Board(deepcopy(current_pieces), board_color_up)
					aux_board.move_piece(index, int(move["position"]))
					minimum = min(self.minimax(aux_board, True, depth - 1, next_turn), minimum)
				
			return minimum
	

	def get_move(self, board):
		move_scores = []
		for move in self.get_all_possible_moves(board):
			score = self.evaluate_move(move, board)
			move_scores.append(score)

		if not move_scores:  # 如果沒有可行的移動
			print("[ERROR] No valid moves available for AI.")
			return None  # 返回空表示無移動可能

		best_score = max(move_scores)
		best_index = move_scores.index(best_score)
		return self.get_all_possible_moves(board)[best_index]



	def get_value(self, board):
		# Receives a Board object, returns a value depending on which player won or which player has the most pieces on board.
		# The value is higher if the board benefits this AI and lower otherwise.
		board_pieces = board.get_pieces()

		if board.get_winner() is not None:
			if board_pieces[0].get_color() == self.color:
				return 2
			else:
				return -2
		
		total_pieces = len(board_pieces)
		player_pieces = len(list(filter(lambda piece: piece.get_color() == self.color, board_pieces)))
		opponent_pieces = total_pieces - player_pieces

		if player_pieces == opponent_pieces:
			return 0
		
		return 1 if player_pieces > opponent_pieces else -1