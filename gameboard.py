pieces = ["p", "l", "n", "s", "g", "b", "r", "k"]
pieces_in_Japanese = ["歩", "香", "桂", "銀", "金", "角", "飛", "玉"]
number_in_Japanese = ["零", "一", "二", "三", "四", "五", "六",  "七", "八", "九", \
    "十", "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八"]
name_in_Japanese = \
        {"p":"歩", "l":"香", "n":"桂", "s":"銀", "g":"金", "b": "角", "r":"飛", \
         "k":"玉", "+p":"と", "+l":"杏", "+n":"圭", "+s":"全", "+b":"馬", "+r":"龍"}
value_of_pieces = {"p":100, "l":300, "n":400, "s":600, "g":700, "b":900, "r":1000, \
    "k":0, "+p":700, "+l":700, "+n":700, "+s":700, "+b":1100, "+r":1200}
INF = 10**9

file = ["9", "8", "7", "6", "5", "4", "3", "2", "1"]
rank = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
file_to_index = {"9":0, "8":1, "7":2, "6":3, "5":4, "4":5, "3":6, "2":7, "1":8}
rank_to_index = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7, "i":8}

class piece:
    def __init__(self, name):
        if name[-1].isupper():
            self.isblack = True
        else:
            self.isblack = False
        name = name.lower()
        self.name = name

class move:
    def __init__(self, i, j, ni, nj, piece_name, promote=0, get=""):
        self._from = (i, j)
        self._to = (ni, nj)
        self.piece_name = piece_name
        self.get = get
        self.promote = promote
        if i == j == -1:
            self.name = f"{piece_name.upper()}*{file[nj]}{rank[ni]}"
        else:
            self.name = f"{file[j]}{rank[i]}{file[nj]}{rank[ni]}{'+'if promote else ''}"

class shogi_board:
    
    def __init__(self, sfen="lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL B - 1"):
        if sfen[:4] == "sfen":
            sfen = sfen[5:]
        sfen_split = sfen.split()
        assert len(sfen_split) == 2 or len(sfen_split) == 4

        board, turn, hand, move_count = sfen_split
        self.move_count = int(move_count)
    
        board += "/"
        self.board = [[]*9 for _ in range(9)]
        idx = 0
        for i in range(9):
            while board[idx] != "/":
                if board[idx] == "+":
                    self.board[i].append(piece(board[idx:idx+2]))
                    idx += 2
                elif board[idx].isalpha():
                    self.board[i].append(piece(board[idx]))
                    idx += 1
                elif board[idx].isdigit():
                    for _ in range(int(board[idx])):
                        self.board[i].append("")
                    idx += 1
                else:
                    assert False

            assert len(self.board[i]) == 9
            idx += 1

        if turn == "B" or turn == "b":
            self.black_turn = 1
        if turn == "W" or turn == "w":
            self.black_turn = 0

        self.black_hand = {"p":0, "l":0, "n":0, "s":0, "g":0, "b":0, "r":0}
        self.white_hand = {"p":0, "l":0, "n":0, "s":0, "g":0, "b":0, "r":0}
        if hand != "-":
            idx = 0
            while idx < len(hand):
                if hand[idx].isnumeric():
                    if hand[idx+1].isnumeric():
                        num = int(hand[idx:idx+2])
                        idx += 2
                    else:
                        num = int(hand[idx:idx+1])
                        idx += 1
                else:
                    num = 1
                if hand[idx].isupper():
                    self.black_hand[hand[idx].lower()] += num
                    idx += 1
                else:
                    self.white_hand[hand[idx]] += num
                    idx += 1

        self.history = []

    def print_in_BOD(self):
        print("後手の持ち駒:", end="")
        if sum(self.white_hand.values()) == 0:
            print("なし")
        else:
            for i in range(7)[::-1]:
                if self.white_hand[pieces[i]] > 0:
                    if self.white_hand[pieces[i]] > 1:
                        print(pieces_in_Japanese[i], end="")
                        print(number_in_Japanese[self.white_hand[pieces[i]]], end="")
                    else:
                        print(pieces_in_Japanese[i], end="")
                    print(" ", end="")
            print()
        print("  ９ ８ ７ ６ ５ ４ ３ ２ １")
        print("+---------------------------+")
        for i in range(9):
            print("|", end="")
            for j in range(9):
                if self.board[i][j] == "":
                    print(" ・", end="")
                else:
                    if self.board[i][j].isblack:
                        print(f" {name_in_Japanese[self.board[i][j].name]}", end="")
                    else:
                        print(f"v{name_in_Japanese[self.board[i][j].name]}", end="")
            print("|", end="")
            print(number_in_Japanese[i+1])
        print("+---------------------------+")
        print("先手の持ち駒:", end="")
        if sum(self.black_hand.values()) == 0:
            print("なし")
        else:
            for i in range(7)[::-1]:
                if self.black_hand[pieces[i]] > 0:
                    print(" ", end="")
                    if self.black_hand[pieces[i]] > 1:
                        print(pieces_in_Japanese[i], end="")
                        print(number_in_Japanese[self.black_hand[pieces[i]]], end="")
                    else:
                        print(pieces_in_Japanese[i], end="")
            print()
    
    def can_enter(self, i, j):
        if i <= -1 or i >= 9 or j <= -1 or j >= 9:
            return False
        if self.board[i][j] == "":
            return True
        if self.black_turn == self.board[i][j].isblack:
            return False
        else:
            return True

    def is_enemy_area(self, i, j):
        if self.black_turn:
            if i <= 2:
                return True
            else:
                return False
        else:
            if i >= 6:
                return True
            else:
                return False

    def yield_moves_from_coordinate(self, i, j, ni, nj):
        if (self.is_enemy_area(i, j) or self.is_enemy_area(ni, nj))\
            and self.board[i][j].name[0] != "+" and self.board[i][j].name not in ["g", "k"]:
            can_promote = 1
        else:
            can_promote = 0
        if self.can_enter(ni, nj):
            if self.board[ni][nj] == "":
                yield move(i, j, ni, nj, self.board[i][j].name)
                if can_promote:
                    yield move(i, j, ni, nj, self.board[i][j].name, 1)
            else:
                yield move(i, j, ni, nj, self.board[i][j].name, get=self.board[ni][nj].name)
                if can_promote:
                    yield move(i, j, ni, nj, self.board[i][j].name, 1, get=self.board[ni][nj].name)

    def moves(self):
        if self.black_turn:
            direction = -1
        else:
            direction = 1
        for i in range(9):
            for j in range(9):
                if self.board[i][j] != "":
                    _piece = self.board[i][j]
                    if self.black_turn != _piece.isblack:
                        continue

                    if _piece.name == "p":
                        ni, nj = i+direction, j
                        for _move in self.yield_moves_from_coordinate(i, j, ni, nj):
                            yield _move

                    if _piece.name == "l":
                        ni, nj = i+direction, j
                        while self.can_enter(ni, nj):
                            for _move in self.yield_moves_from_coordinate(i, j, ni, nj):
                                yield _move
                            if self.board[ni][nj] != "":
                                break
                            ni += direction

                    if _piece.name == "n":
                        for ni, nj in [(i+2*direction, j-1), (i+2*direction, j+1)]:
                            for _move in self.yield_moves_from_coordinate(i, j, ni, nj):
                                yield _move
                    
                    if _piece.name == "s":
                        for ni, nj in [(i+direction, j), (i+direction, j-1), (i+direction, j+1), \
                            (i-direction, j-1), (i-direction, j+1)]:
                            for _move in self.yield_moves_from_coordinate(i, j, ni, nj):
                                yield _move

                    if _piece.name in ["g", "+p", "+l", "+n", "+s"]:
                        for ni, nj in [(i+direction, j), (i+direction, j-1), (i+direction, j+1), \
                            (i, j-1), (i, j+1), (i-direction, j)]:
                            for _move in self.yield_moves_from_coordinate(i, j, ni, nj):
                                yield _move

                    if _piece.name[-1] == "b":
                        ni, nj = i+direction, j-1
                        while self.can_enter(ni, nj):
                            for _move in self.yield_moves_from_coordinate(i, j, ni, nj):
                                yield _move
                            if self.board[ni][nj] != "":
                                break
                            ni += direction
                            nj -= 1

                        ni, nj = i+direction, j+1
                        while self.can_enter(ni, nj):
                            for _move in self.yield_moves_from_coordinate(i, j, ni, nj):
                                yield _move
                            if self.board[ni][nj] != "":
                                break
                            ni += direction
                            nj += 1

                        ni, nj = i-direction, j-1
                        while self.can_enter(ni, nj):
                            for _move in self.yield_moves_from_coordinate(i, j, ni, nj):
                                yield _move
                            if self.board[ni][nj] != "":
                                break
                            ni -= direction
                            nj -= 1

                        ni, nj = i-direction, j+1
                        while self.can_enter(ni, nj):
                            for _move in self.yield_moves_from_coordinate(i, j, ni, nj):
                                yield _move
                            if self.board[ni][nj] != "":
                                break
                            ni -= direction
                            nj += 1
                        if _piece.name[0] == "+":
                            for ni, nj in [(i+direction, j), (i, j-1), (i, j+1), (i-direction, j)]:
                                for _move in self.yield_moves_from_coordinate(i, j, ni, nj):
                                    yield _move
                    
                    if _piece.name[-1] == "r":
                        ni, nj = i+direction, j
                        while self.can_enter(ni, nj):
                            for _move in self.yield_moves_from_coordinate(i, j, ni, nj):
                                yield _move
                            if self.board[ni][nj] != "":
                                break
                            ni += direction

                        ni, nj = i, j-1
                        while self.can_enter(ni, nj):
                            for _move in self.yield_moves_from_coordinate(i, j, ni, nj):
                                yield _move
                            if self.board[ni][nj] != "":
                                break
                            nj -= 1

                        ni, nj = i, j+1
                        while self.can_enter(ni, nj):
                            for _move in self.yield_moves_from_coordinate(i, j, ni, nj):
                                yield _move
                            if self.board[ni][nj] != "":
                                break
                            nj += 1

                        ni, nj = i-direction, j
                        while self.can_enter(ni, nj):
                            for _move in self.yield_moves_from_coordinate(i, j, ni, nj):
                                yield _move
                            if self.board[ni][nj] != "":
                                break
                            ni -= direction

                        if _piece.name[0] == "+":
                            for ni, nj in [(i+direction, j-1), (i+direction, j+1), (i-direction, j-1), (i-direction, j+1)]:
                                for _move in self.yield_moves_from_coordinate(i, j, ni, nj):
                                    yield _move
                    
                    if _piece.name == "k":
                        for ni, nj in [(i+direction, j), (i+direction, j-1), (i+direction, j+1), \
                            (i, j-1), (i, j+1), (i-direction, j), (i-direction, j-1), (i-direction, j+1)]:
                            for _move in self.yield_moves_from_coordinate(i, j, ni, nj):
                                yield _move

        if self.black_turn:
            for piece_name in self.black_hand:
                if self.black_hand[piece_name] > 0:
                    for ni in range(9):
                        for nj in range(9):
                            if self.board[ni][nj] == "":
                                yield move(-1, -1, ni, nj, piece_name)
        
        else:
            for piece_name in self.white_hand:
                if self.white_hand[piece_name] > 0:
                    for ni in range(9):
                        for nj in range(9):
                            if self.board[ni][nj] == "":
                                yield move(-1, -1, ni, nj, piece_name)
        
    def legal_moves(self):
        for _move in self.moves():
            self.append(_move)
            legal = self.legal()
            self.pop()
            if legal:
                yield _move

    def legal(self):
        for j in range(9): #二歩
            black_count = 0
            white_count = 0
            for i in range(9):
                if self.board[i][j] != "" and self.board[i][j].name == "p":
                    if self.board[i][j].isblack:
                        black_count += 1
                    else:
                        white_count += 1
            if black_count >= 2 or white_count >= 2:
                return False

        for j in range(9): #行き所のない駒
            if self.board[0][j] != "":
                _piece = self.board[0][j]
                if _piece.isblack and _piece.name in ["p", "l", "n"]:
                    return False
            if self.board[1][j] != "":
                _piece = self.board[1][j]
                if _piece.isblack and _piece.name == "n":
                    return False
            if self.board[7][j] != "":
                _piece = self.board[7][j]
                if not _piece.isblack and _piece.name == "n":
                    return False
            if self.board[8][j] != "":
                _piece = self.board[8][j]
                if not _piece.isblack and _piece.name in ["p", "l", "n"]:
                    return False

        for _move in self.moves(): #王手放置
            ni, nj = _move._to
            if self.board[ni][nj] != "" and self.board[ni][nj].name == "k":
                return False
        return True

    def append(self, _move):
        self.history.append(_move)
        i, j = _move._from
        ni, nj = _move._to
        if (i, j) == (-1, -1):
            if self.black_turn:
                self.black_hand[_move.piece_name] -= 1
                self.board[ni][nj] = piece(_move.piece_name.upper())
            else:
                self.white_hand[_move.piece_name] -= 1
                self.board[ni][nj] = piece(_move.piece_name)
        else:
            if _move.get != "":
                if self.black_turn:
                    self.black_hand[_move.get[-1]] += 1
                else:
                    self.white_hand[_move.get[-1]] += 1
            self.board[ni][nj] = self.board[i][j]
            if _move.promote:
                self.board[ni][nj].name = "+" + self.board[ni][nj].name
            self.board[i][j] = ""
        
        self.move_count += 1
        self.black_turn ^= 1

    def pop(self):
        _move = self.history.pop()
        i, j = _move._from
        ni, nj = _move._to

        self.black_turn ^= 1
        if (i, j) == (-1, -1):
            if self.black_turn:
                self.black_hand[_move.piece_name] += 1
                self.board[ni][nj] = ""
            else:
                self.white_hand[_move.piece_name] += 1
                self.board[ni][nj] = ""
        else:
            self.board[i][j] = self.board[ni][nj]
            if _move.promote:
                self.board[i][j].name = self.board[i][j].name[1:]
            if _move.get != "":
                if self.black_turn:
                    self.black_hand[_move.get[-1]] -= 1
                    self.board[ni][nj] = piece(_move.get)
                else:
                    self.white_hand[_move.get[-1]] -= 1
                    self.board[ni][nj] = piece(_move.get.upper())
            else:
                self.board[ni][nj] = ""
        self.move_count -= 1

    def usi_to_move(self, string):
        get = ""
        promote = 0
        if string[0].isupper():
            i = -1
            j = -1
            ni = rank_to_index[string[3]]
            nj = file_to_index[string[2]]
            piece_name = string[0].lower()
        else:
            i = rank_to_index[string[1]]
            j = file_to_index[string[0]]
            ni = rank_to_index[string[3]]
            nj = file_to_index[string[2]]
            if self.board[ni][nj] != "":
                get = self.board[ni][nj].name
            piece_name = self.board[i][j].name
            if string[-1] == "+":
                promote = 1
        return move(i, j, ni, nj, piece_name, promote, get)

    def evaluate(self):
        score = 0
        for i in range(9):
            for j in range(9):
                if self.board[i][j] != "":
                    if self.board[i][j].isblack:
                        score += value_of_pieces[self.board[i][j].name]
                    else:
                        score -= value_of_pieces[self.board[i][j].name]
        
        for _piece in self.black_hand:
            score += value_of_pieces[_piece]*self.black_hand[_piece]
        for _piece in self.white_hand:
            score -= value_of_pieces[_piece]*self.white_hand[_piece]
        return score
