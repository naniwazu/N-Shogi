import gameboard
from random import choice

while True:
    command = input()
    if command == "usi":
        print("id name N-Shogi")
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
        for move in legal_moves:
            print(move.name)
        if len(legal_moves) == 0: 
            print("bestmove resign")
        else:
            next_move = choice(legal_moves)
            print(f"bestmove {next_move.name}")
