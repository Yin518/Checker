from piece import Piece
from board import Board
from board_gui import BoardGUI
from held_piece import HeldPiece
from ai import AI
from utils import get_surface_mouse_offset, get_piece_position

class GameControl:
    def __init__(self, player_color, is_computer_opponent):
        self.turn = player_color
        self.winner = None
        self.board = None
        self.board_draw = None
        self.held_piece = None
        self.ai_control = None

        if is_computer_opponent:
            self.ai_control = AI("B") if player_color == "W" else AI("W")

        self.setup()

    def get_turn(self):
        return self.turn

    def get_winner(self):
        return self.winner

    def setup(self):
        # Initial setup
        pieces = []

        for opponent_piece in range(0, 12):
            pieces.append(Piece(str(opponent_piece) + 'BN'))
        
        for player_piece in range(20, 32):
            pieces.append(Piece(str(player_piece) + 'WN'))
        
        self.board = Board(pieces, self.turn)
        self.board_draw = BoardGUI(self.board)        
        pass
    
    def draw_screen(self, display_surface):
        self.board_draw.draw_board(display_surface)
        self.board_draw.draw_pieces(display_surface)

        if self.held_piece is not None:
            self.held_piece.draw_piece(display_surface)

    def hold_piece(self, mouse_pos):
        piece_clicked = self.board_draw.get_piece_on_mouse(mouse_pos)
        board_pieces = self.board.get_pieces()
        has_jump_restraint = False # True if any piece can jump in one of its moves, forcing the player to jump

        if piece_clicked is None:
            return
        
        if piece_clicked["piece"]["color"] != self.turn:
            return
        
        # Determines if player has a jump restraint
        for piece in board_pieces:
            for move in piece.get_moves(self.board):
                if move["eats_piece"]:
                    if piece.get_color() == piece_clicked["piece"]["color"]:
                        has_jump_restraint = True
            else:
                continue
            break
        
        piece_moves = board_pieces[piece_clicked["index"]].get_moves(self.board)

        if has_jump_restraint:
            piece_moves = list(filter(lambda move: move["eats_piece"] == True, piece_moves))

        move_marks = []

        # Gets possible moving positions and tells BoardGUI to draw them
        for possible_move in piece_moves:
            row = self.board.get_row_number(int(possible_move["position"]))
            column = self.board.get_col_number(int(possible_move["position"]))
            move_marks.append((row, column))

        self.board_draw.set_move_marks(move_marks)

        self.board_draw.hide_piece(piece_clicked["index"])
        self.set_held_piece(piece_clicked["index"], board_pieces[piece_clicked["index"]], mouse_pos)
    
    def release_piece(self, pos):
        if self.winner:  # �p�G��Ĺ�a�A����i�@�B�ާ@
            print(f"Game over. {self.winner} wins!")
            return None
    
        if self.held_piece is None:
            return None  # �L���I���A���������ާ@

        position_released = self.held_piece.check_collision(self.board_draw.get_move_marks())
        moved_index = self.board_draw.show_piece()
        piece_moved = self.board.get_piece_by_index(moved_index)

        if position_released is not None:
            self.board.move_piece(moved_index, self.board_draw.get_position_by_rect(position_released))
            self.board_draw.set_pieces(self.board_draw.get_piece_properties(self.board))
            self.winner = self.board.get_winner()

            # �T�{�O�_���s��Y�Ѿ��|�]���Y����^
            jump_moves = list(filter(lambda move: move["eats_piece"] == True, piece_moved.get_moves(self.board)))
            if len(jump_moves) == 0 or not piece_moved.get_has_eaten():
                # �u����S���s��Y�ѮɡA�~�����^�X
                self.turn = "B" if self.turn == "W" else "W"

        self.held_piece = None
        self.board_draw.set_move_marks([])

        # �p�GAI�O�U�@�Ӧ^�X�A�h��AI�۰ʤU��
        if self.turn == "B" and self.ai_control:
            self.move_ai()

    def set_held_piece(self, index, piece, mouse_pos):
        # Creates a HeldPiece object to follow the mouse
        surface = self.board_draw.get_surface(piece)
        offset = get_surface_mouse_offset(self.board_draw.get_piece_by_index(index)["rect"], mouse_pos)
        self.held_piece = HeldPiece(surface, offset)

    def move_ai(self):
        while self.turn == "B":
            move = self.ai.get_move(self.board)
            if not move:
                print("[DEBUG] No valid moves for AI. Ending turn.")
                break

            self.board.move_piece(move["from_index"], move["to_index"])
            self.board_draw.set_pieces(self.board_draw.get_piece_properties(self.board))

            # �ˬd�O�_�i�H�s��Y
            piece = self.board.get_piece_by_index(move["to_index"])
            jump_moves = list(filter(lambda move: move["eats_piece"], piece.get_moves(self.board)))

            if not jump_moves or not piece.get_has_eaten():  # �L�k�s��Y�ΦY�l����
                self.turn = "W"  # �����쪱�a�^�X
                break

    def update_game_state(self, move_data):
        # ���a�^�X�B�z
        if self.turn == "W":
            success = self.board.move_piece(move_data["from_index"], move_data["to_index"])
            if not success:
                print("[ERROR] Move failed. Invalid move.")
                return  # �L�Ĳ��ʡA������^
                
            self.board_draw.set_pieces(self.board_draw.get_piece_properties(self.board))
            self.winner = self.board.get_winner()

            # �P�_�O�_�ݭn�O�d���a�^�X
            piece = self.board.get_piece_by_index(move_data["to_index"])
            jump_moves = list(filter(lambda move: move["eats_piece"], piece.get_moves(self.board)))

            if piece.get_has_eaten() and len(jump_moves) > 0:
                print("[DEBUG] Player retains turn for continuous jump.")
                return  # �O�d���a�^�X

            # ������ AI �^�X
            self.turn = "B"

        # AI �^�X�B�z
        elif self.turn == "B" and self.ai_control:
            self.move_ai()

        # �P�B�C�����A
        self.sync_game_state()
