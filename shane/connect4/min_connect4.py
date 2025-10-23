COLORS = [ 'R', 'Y' ]
MAX_ROW = 6
MAX_COL = 7  # should be < 10
PLAYER_ONE = 0

def to_board(bitboard):
    board = [ [ '.' for col in range(MAX_COL) ] for row in range(MAX_ROW) ]
    for row in range(MAX_ROW):
        for col in range(MAX_COL):
            i = row * 10 + col
            mask = 1 << i
            for c,color in enumerate(COLORS):
                if bitboard[c] & mask:  board[row][col] = color
    return board


def disp_bitboard(bitboard):
    board = to_board(bitboard)
    print('  ' + ''.join([str(col) for col in range(MAX_COL)]))
    for row in range(MAX_ROW):
        print(row, ''.join(board[row]))
    return


def blank_bitboard():
    bitboard = { 0:0, 1:0 }
    return bitboard
    return bitboard


def add_piece(bitboard, c, col):
    # find first empty row in column
    all = bitboard[0] | bitboard[1]
    move_mask = 1 << (((MAX_ROW - 1) * 10) + col)
    while (move_mask and (all & move_mask)):  move_mask >>= 10
    bitboard[c] |= move_mask
    return move_mask


def log2(z):
    # return z.bit_length()  # slow!
    i = -1
    while z:
        z >>= 1
        i += 1
    return i


def check_win_color(b):
    # check - horizontal
    y = b & (b << 2)
    z = (y & (y << 1)) 
    if (z):  return z, '-'
    # check / diagonal
    y = b & (b << 18)
    z = (y & (y << 9)) 
    if (z):  return z, '/'
    # check | vertical
    y = b & (b << 20)
    z = (y & (y << 10)) 
    if (z):  return z, '|'
    # check \ diagonal
    y = b & (b << 22)
    z = (y & (y << 11)) 
    if (z):  return z, '\\'
    return 0, None


def eval_bitboard(bitboard, move_mask, to_move, col):
    col_scores = [ 1, 0, 3, 5, 3, 0, 1 ]
    i = log2(move_mask)
    adj_mask = (0b111 << 0) | (0b111 << 10) | (0b111 << 20)  # equiv i=11
    try:
        adj_mask <<= (i - 11)
    except:
        adj_mask >>= (11 - i)
    adj_mask = bitboard[to_move] & adj_mask
    adj_count = adj_mask.bit_count()
    score = col_scores[col] + adj_count
    return score if (to_move == PLAYER_ONE) else -score


def recurse_moves(p_bitboard, p_to_move, p_depth):
    # generate bitboards for each col and check for win (we do not have to eval other cols if win)
    c_bitboards = [ None for c in range(MAX_COL) ]
    c_move_masks = [ 0 for c in range(MAX_COL) ]
    c_scores = [ None for c in range(MAX_COL) ]
    cols = []
    for col in range(MAX_COL):
        c_bitboard = dict(p_bitboard)  # copy
        c_move_mask = add_piece(c_bitboard, p_to_move, col)
        if (c_move_mask):  # if valid move
            # check for win
            b = c_bitboard[p_to_move]
            c_win_mask, direction = check_win_color(b)
            if c_win_mask:
                score = 100 - p_depth
                c_scores[col] = score if (p_to_move == PLAYER_ONE) else -score  
                return c_scores  # found win, do not need any other moves
            # save child for recursion
            c_bitboards[col] = c_bitboard
            c_move_masks[col] = c_move_mask
            cols.append(col)
    # evaluate each move and recurse if needed
    c_depth = p_depth + 1
    c_to_move = 1 if p_to_move == 0 else 0
    MAX_DEPTH = 6
    move_count = p_bitboard[0].bit_count()
    MAX_DEPTH += (move_count // 5)
    for col in cols:
        c_bitboard = c_bitboards[col]
        # if not max depth
        if (c_depth < MAX_DEPTH):
            r_scores = recurse_moves(c_bitboard, c_to_move, c_depth)
            r_scores = [ s for s in r_scores if s != None ]
            # parent gets minmax of children
            score = 0
            if r_scores:
                score = max(r_scores) if c_to_move == PLAYER_ONE else min(r_scores)
            c_scores[col] = score
            # if we found a forced winning move at depth for color to move, we can stop
            if (p_to_move == PLAYER_ONE):
                if (score > 50):  break
            elif (score < -50):  break
        else:
            # hit leaf (max depth) of tree
            c_move_mask = c_move_masks[col]
            score = eval_bitboard(c_bitboard, c_move_mask, p_to_move, col)
            c_scores[col] = score
    return c_scores


# convert color_list to bitboard
# in color_list 0,0 is bottom/left of board
def to_bitboard(color_list):
    bitboard = blank_bitboard()
    for row in range(MAX_ROW):
        for col in range(MAX_COL):
            get_i = (6 - row - 1) * 8 + (7 - col - 1) + 1
            get_mask = 1 << get_i
            set_i = row * 10 + col
            set_mask = 1 << set_i
            for c in range(2):
                if color_list[c]['bitmap'] & get_mask:  bitboard[c] |= set_mask
    return bitboard


def get_move(color_list, to_move):
    global PLAYER_ONE
    PLAYER_ONE = to_move
    bitboard = to_bitboard(color_list)
    c_scores = recurse_moves(bitboard, to_move, 0)
    min_col = None
    max_col = None
    min_s = None
    max_s = None
    for c,s in enumerate(c_scores):
        if s != None:
            if min_col == None:  min_col,min_s = c,s
            if max_col == None:  max_col,max_s = c,s
            if s < min_s:  min_col,min_s = c,s
            if s > max_s:  max_col,max_s = c,s
    disp_bitboard(bitboard)
    print(c_scores)
    return max_col if to_move == PLAYER_ONE else min_col

