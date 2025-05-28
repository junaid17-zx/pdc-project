import socket
import threading
import json

class TicTacToeServer:
    def __init__(self, host='localhost', port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(2)
        self.clients = {}  # client: symbol
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.game_over = False

        print("Server started. Waiting for connections...")
        self.accept_connections()

    def accept_connections(self):
        symbols = ["X", "O"]
        while len(self.clients) < 2:
            client, addr = self.server.accept()
            symbol = symbols[len(self.clients)]
            self.clients[client] = symbol
            client.send(json.dumps({'type': 'role', 'symbol': symbol}).encode('utf-8'))
            print(f"Player {symbol} connected from {addr}")
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if message:
                    self.process_message(message, client)
            except:
                if client in self.clients:
                    del self.clients[client]
                break

    def process_message(self, message, client):
        data = json.loads(message)
        if data['type'] == 'move' and not self.game_over:
            self.handle_move(data['row'], data['col'], client)
        elif data['type'] == 'chat':
            self.broadcast_chat(data['message'], self.clients[client])
        elif data['type'] == 'reset':
            self.reset_game()

    def handle_move(self, row, col, client):
        symbol = self.clients[client]
        if symbol != self.current_player or self.board[row][col] != "":
            return  # invalid move

        self.board[row][col] = symbol
        winner, winning_line = self.check_winner()
        if winner:
            self.game_over = True
            self.broadcast(json.dumps({
                'type': 'winner',
                'player': symbol,
                'winning_line': winning_line,
                'board': self.board
            }))
        elif self.check_draw():
            self.game_over = True
            self.broadcast(json.dumps({
                'type': 'draw',
                'board': self.board
            }))
        else:
            self.current_player = "O" if self.current_player == "X" else "X"
            self.broadcast(json.dumps({
                'type': 'update',
                'board': self.board,
                'current_player': self.current_player
            }))

    def broadcast(self, message):
        for client in list(self.clients):
            try:
                client.send(message.encode('utf-8'))
            except:
                del self.clients[client]

    def broadcast_chat(self, message, sender_symbol):
        for client in list(self.clients):
            try:
                client.send(json.dumps({
                    'type': 'chat',
                    'message': f"[{sender_symbol}] {message}"
                }).encode('utf-8'))
            except:
                del self.clients[client]

    def reset_game(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.game_over = False
        self.broadcast(json.dumps({
            'type': 'reset',
            'board': self.board,
            'current_player': self.current_player
        }))

    def check_winner(self):
        lines = [
            [(0,0),(0,1),(0,2)],
            [(1,0),(1,1),(1,2)],
            [(2,0),(2,1),(2,2)],
            [(0,0),(1,0),(2,0)],
            [(0,1),(1,1),(2,1)],
            [(0,2),(1,2),(2,2)],
            [(0,0),(1,1),(2,2)],
            [(0,2),(1,1),(2,0)]
        ]
        for line in lines:
            c1, c2, c3 = line
            if (self.board[c1[0]][c1[1]] == self.board[c2[0]][c2[1]] == self.board[c3[0]][c3[1]] != ""):
                return True, line
        return False, None

    def check_draw(self):
        return all(cell != "" for row in self.board for cell in row)

if __name__ == "__main__":
    TicTacToeServer()
