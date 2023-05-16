class Player:
    """Base player class"""
    def __init__(self, symbol):
        self.symbol = symbol

    def get_symbol(self):
        return self.symbol
    
    def get_move(self, board):
        raise NotImplementedError()



class HumanPlayer(Player):
    """Human subclass with text input in command line"""
    def __init__(self, symbol):
        Player.__init__(self, symbol)
        self.total_nodes_seen = 0

    def clone(self):
        return HumanPlayer(self.symbol)
        
    def get_move(self, board):
        col = int(input("Enter col:"))
        row = int(input("Enter row:"))
        return  (col, row)


class AlphaBetaPlayer(Player):
    """Class for Alphabeta AI: implement functions minimax, eval_board, get_successors, get_move
    eval_type: int
        0 for H0, 1 for H1, 2 for H2
    prune: bool
        1 for alpha-beta, 0 otherwise
    max_depth: one move makes the depth of a position to 1, search should not exceed depth
    total_nodes_seen: used to keep track of the number of nodes the algorithm has seearched through
    symbol: X for player 1 and O for player 2
    """
    def __init__(self, symbol, eval_type, prune, max_depth):
        Player.__init__(self, symbol)
        self.eval_type = eval_type
        self.prune = prune
        self.max_depth = int(max_depth) 
        self.max_depth_seen = 0
        self.total_nodes_seen = 0
        if symbol == 'X':
            self.oppSym = 'O'
        else:
            self.oppSym = 'X'


    def terminal_state(self, board):
        # If either player can make a move, it's not a terminal state
        for c in range(board.cols):
            for r in range(board.rows):
                if board.is_legal_move(c, r, "X") or board.is_legal_move(c, r, "O"):
                    return False 
        return True 


    def terminal_value(self, board):
        # Regardless of X or O, a win is float('inf')
        state = board.count_score(self.symbol) - board.count_score(self.oppSym)
        if state == 0:
            return 0
        elif state > 0:
            return float('inf')
        else:
            return -float('inf')


    def flip_symbol(self, symbol):
        # Short function to flip a symbol
        if symbol == "X":
            return "O"
        else:
            return "X"


    def max_val(self, board, alpha, beta, depth):

        self.max_depth_seen = max(self.max_depth_seen, depth) #if this is the new deepest we've seen, update it

        if depth == 0 or self.terminal_state(board): #if the depth is 0 or we hit a terminal state
            return self.eval_board(board), None, None #return the weight of that node

        max_eval = float('-inf')

        max_row = None
        max_col = None #these are to return the col and row of the best choice. idk if its necessary

        for successor in self.get_successors(board, self.symbol): #check all of the children
            self.total_nodes_seen += 1 #increase the number of nodes we have seen by 1

            eval, col, row = self.min_val(successor, alpha, beta, depth - 1)
            if eval >= max_eval:
                max_eval = eval
                max_col, max_row = successor.move

                #print("min returning row: ", max_row, "and col: ", max_col)
                alpha = max(alpha, max_eval) #update alpha

            if alpha >= beta and self.prune == '1': #this is the pruning happening. breaks for loop
                return max_eval, max_col, max_row

            # alpha = max(alpha, max_eval) 

        #print("min returning row: ", max_row, "and col: ", max_col)
        return max_eval, max_col, max_row


    def min_val(self, board, alpha, beta, depth):  
        self.max_depth_seen = max(self.max_depth_seen, depth) #if this is the new deepest we've seen, update it

        if depth == 0 or self.terminal_state(board): #if the depth is 0 or we hit a terminal state
            return self.eval_board(board), None, None #return value of that node
        
        min_eval = float('inf')
        min_row = None
        min_col = None

        for successor in self.get_successors(board, self.oppSym): #check all of the children
            self.total_nodes_seen += 1
            eval, row, col = self.max_val(successor, alpha, beta, depth - 1)
            if eval <= min_eval:
                min_eval = eval
                min_col, min_row = successor.move
                beta = min(beta, min_eval)

            if alpha >= beta and self.prune == '1': #this is the pruning happening 
                return min_eval, min_col, min_row

            # beta = min(beta, min_eval) #ccan't have it out here as originally thought, because we only update if it is lower
        #print("min returning row: ", min_row, "and col: ", min_col)
        return min_eval, min_col, min_row


    def alphabeta(self, board):
        # Write minimax function here using eval_board and get_successors
        # type:(board) -> (int, int)
        col = None
        row = None
        depth = self.max_depth #this is the depth that we will search too. 

        _, col, row = self.max_val(board, float('-inf'), float('inf'), depth - 1)

        #print("returning row: ", row, "and col", col)
        return (col, row) #I think it must be returned like this


    def eval_board(self, board): 
        #print("self.eval type is ", self.eval_type)
        # Write eval function here
        # type:(board) -> (float)
        value = 0
        if self.eval_type == "0":
            self_score = board.count_score(self.symbol) #use built in function to count # tiles for the player checking score
            opponent_score = board.count_score(self.oppSym) #use built in to check opponents tiles
            
            value = self_score - opponent_score
        elif self.eval_type == "1":
            self_legalMoves = 0
            opp_legalMoves = 0
            for col in range(board.get_num_cols()): #loop through. check each box and see if it is a legal move for either player. if it is, increment their tally
                for row in range(board.get_num_rows()):
                    if board.is_legal_move(col, row, self.symbol):
                        self_legalMoves += 1
                    if board.is_legal_move(col, row, self.oppSym):
                        opp_legalMoves += 1
            
            value = self_legalMoves - opp_legalMoves#return the difference 
            
        elif self.eval_type == "2":
            self_val = 0
            opp_val = 0
            safety_vals = [     #this is a weighted representation of the worth of each location. the worth is based off of how easy it is to capture that spot. this heuristic will try to find the most worth boards possible for the ai
                [2, 1, 1, 2],
                [1, 0, 0, 1],
                [1, 0, 0, 1],
                [2, 1, 1, 2],
            ]
            for col in range(board.get_num_cols()): #loop through. check each box and see if it is a legal move for either player. if it is, increment their tally
                for row in range(board.get_num_rows()):
                    if board.get_cell(col, row) == self.symbol:
                        self_val += safety_vals[col][row]
                    if board.get_cell(col, row) == self.oppSym:
                        opp_val += safety_vals[col][row]
            value = self_val - opp_val

        #print("eval board returning :", value)
        return value


    def get_successors(self, board, player_symbol):
        # Write function that takes the current state and generates all successors obtained by legal moves
        # type:(board, player_symbol) -> (list)
        successors = [] #list of successors
        for col in range(board.get_num_cols()):
            for row in range(board.get_num_rows()):
                if board.is_legal_move(col, row, player_symbol): #check if that position is a legal move for the player. 
                    successor = board.cloneOBoard()              #make a clone of the current board
                    successor.play_move(col, row, player_symbol) #apply the legal move to the board
                    successor.move = (col, row) #was missing this for days and nothing was workin lel
                    successors.append(successor)                 #add the potential board state to the list of successors
        return successors


    def get_move(self, board):
        # Write function that returns a move (column, row) here using minimax
        # type:(board) -> (int, int)
        return self.alphabeta(board)

       
        
#HAHAHHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAh




