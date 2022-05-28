import gameboard
from random import choice

while True:
    command = input()
    if command == "usi":
        print("id name N-Shogi1")
        print("id author naniwazu")
        print("usiok")
    if command == "isready":
        print("readyok")
    if command == "quit":
        break
    if command[:8] == "position":
        command = command[9:]
        if "moves" in command:
            sfen, moves = command.split(" moves ")
            if sfen == "startpos":
                current_board = gameboard.shogi_board()
            else:
                current_board = gameboard.shogi_board(sfen)
            moves = list(moves.split())
            for string in moves:
                move = current_board.usi_to_move(string)
                current_board.append(move)
        else:
            sfen = command
            if sfen == "startpos":
                current_board = gameboard.shogi_board()
            else:
                current_board = gameboard.shogi_board(sfen)

    if command[:2] == "go":
        command = command[3:]
        if command[:6] == "ponder":
            continue
        legal_moves = list(current_board.legal_moves())
        if len(legal_moves) == 0: 
            print("bestmove resign")
        else:
            if current_board.black_turn:
                factor = 1
            else:
                factor = -1
            bestmoves = ["resign"]
            bestscore = -10**9
            for next_move in legal_moves:
                current_board.append(next_move)
                score = current_board.evaluate()*factor
                if score > bestscore:
                    bestmoves = [next_move.name]
                    bestscore = score
                elif score == bestscore:
                    bestmoves.append(next_move.name)
                current_board.pop()
            bestmove = choice(bestmoves)
            print(f"bestmove {bestmove}")