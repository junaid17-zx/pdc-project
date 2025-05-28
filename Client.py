import tkinter as tk
from tkinter import messagebox
import socket
import threading
import json
import time

class AdvancedTicTacToeClient:
    def __init__(self, root, host='localhost', port=12345):
        self.root = root
        self.root.title("Advanced Tic Tac Toe with Chat")
        self.root.geometry("900x600")
        self.root.configure(bg="#1e1e2f")

        self.player_symbol = None
        self.current_turn = "X"
        self.game_over = False
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.winning_line = None

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((host, port))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to server: {e}")
            root.destroy()
            return

        self.cell_size = 140
        self.padding = 20
        self.canvas_size = self.cell_size * 3 + self.padding * 2

        self.left_frame = tk.Frame(root, bg="#1e1e2f")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)

        self.right_frame = tk.Frame(root, bg="#1e1e2f")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(self.left_frame, width=self.canvas_size, height=self.canvas_size, bg="#282c44", highlightthickness=0)
        self.canvas.pack()

        self.status_label = tk.Label(self.left_frame, text="Waiting for role assignment...", font=("Segoe UI", 18, "bold"),
                                     fg="#f0f0f0", bg="#1e1e2f")
        self.status_label.pack(pady=15)

        self.reset_btn = tk.Button(self.left_frame, text="Reset Game", font=("Segoe UI", 14), bg="#4a69bd",
                                   fg="white", relief="flat", activebackground="#6a8ddd",
                                   command=self.send_reset)
        self.reset_btn.pack(pady=10, ipadx=10, ipady=5)

        chat_label = tk.Label(self.right_frame, text="Chat", font=("Segoe UI", 16, "bold"), fg="#f0f0f0", bg="#1e1e2f")
        chat_label.pack(anchor="w")

        self.chat_display_frame = tk.Frame(self.right_frame, bg="#1e1e2f")
        self.chat_display_frame.pack(pady=(10,5), fill=tk.BOTH, expand=True)

        self.chat_canvas = tk.Canvas(self.chat_display_frame, bg="#282c44", highlightthickness=0)
        self.chat_scrollbar = tk.Scrollbar(self.chat_display_frame, orient="vertical", command=self.chat_canvas.yview)
        self.chat_inner_frame = tk.Frame(self.chat_canvas, bg="#282c44")

        self.chat_inner_frame.bind("<Configure>",
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))

        self.chat_canvas.create_window((0, 0), window=self.chat_inner_frame, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=self.chat_scrollbar.set)

        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        entry_frame = tk.Frame(self.right_frame, bg="#1e1e2f")
        entry_frame.pack(fill=tk.X, pady=5)

        self.chat_entry = tk.Entry(entry_frame, font=("Segoe UI", 12))
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))

        self.send_button = tk.Button(entry_frame, text="Send", font=("Segoe UI", 12), bg="#4a69bd",
                                     fg="white", relief="flat", activebackground="#6a8ddd",
                                     command=self.send_chat)
        self.send_button.pack(side=tk.RIGHT)

        self.chat_entry.bind("<Return>", lambda event: self.send_chat())

        self.canvas.bind("<Button-1>", self.click)

        self.draw_grid()

        threading.Thread(target=self.receive_messages, daemon=True).start()

    def draw_grid(self):
        self.canvas.delete("all")
        line_color = "#6a6f89"
        offset = self.padding
        for i in range(1, 3):
            x = offset + i * self.cell_size
            self.canvas.create_line(x, offset, x, self.canvas_size - offset, fill=line_color, width=4)
            y = offset + i * self.cell_size
            self.canvas.create_line(offset, y, self.canvas_size - offset, y, fill=line_color, width=4)

        for r in range(3):
            for c in range(3):
                if self.board[r][c] == "X":
                    self.draw_x(r, c)
                elif self.board[r][c] == "O":
                    self.draw_o(r, c)

    def draw_x(self, row, col):
        offset = self.padding
        x1 = offset + col * self.cell_size + 20
        y1 = offset + row * self.cell_size + 20
        x2 = x1 + self.cell_size - 40
        y2 = y1 + self.cell_size - 40
        self.canvas.create_line(x1, y1, x2, y2, fill="#ff4757", width=10)
        self.canvas.create_line(x1, y2, x2, y1, fill="#ff4757", width=10)

    def draw_o(self, row, col):
        offset = self.padding
        x = offset + col * self.cell_size + self.cell_size / 2
        y = offset + row * self.cell_size + self.cell_size / 2
        radius = (self.cell_size - 40) / 2
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline="#1dd1a1", width=10)

    def click(self, event):
        if self.game_over or not self.player_symbol or self.player_symbol != self.current_turn:
            return

        offset = self.padding
        x, y = event.x, event.y

        if x < offset or y < offset or x > self.canvas_size - offset or y > self.canvas_size - offset:
            return

        col = (x - offset) // self.cell_size
        row = (y - offset) // self.cell_size

        if self.board[row][col] == "":
            self.send_move(row, col)

    def send_move(self, row, col):
        try:
            message = json.dumps({'type': 'move', 'row': row, 'col': col})
            self.client_socket.send(message.encode('utf-8'))
        except Exception as e:
            self.append_chat_message(f"Error sending move: {e}", sent=False)

    def send_reset(self):
        try:
            message = json.dumps({'type': 'reset'})
            self.client_socket.send(message.encode('utf-8'))
        except Exception as e:
            self.append_chat_message(f"Error sending reset: {e}", sent=False)

    def send_chat(self):
        message = self.chat_entry.get().strip()
        if message:
            try:
                self.client_socket.send(json.dumps({'type': 'chat', 'message': message}).encode('utf-8'))
                self.chat_entry.delete(0, tk.END)
            except Exception as e:
                self.append_chat_message(f"Error sending chat: {e}", sent=False)

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(4096).decode('utf-8')
                if message:
                    self.process_message(message)
            except Exception:
                self.append_chat_message("Disconnected from server.", sent=False)
                break

    def process_message(self, message):
        try:
            data = json.loads(message)
        except:
            self.append_chat_message("Invalid message from server.", sent=False)
            return

        if data['type'] == 'role':
            self.player_symbol = data['symbol']
            self.status_label.config(text=f"You are Player {self.player_symbol}", fg="#feca57")
        elif data['type'] == 'update':
            self.board = data['board']
            self.current_turn = data['current_player']
            self.draw_grid()
            self.status_label.config(text=f"Player {self.current_turn}'s turn", fg="#f0f0f0")
        elif data['type'] == 'winner':
            self.board = data.get('board', self.board)
            self.current_turn = data['player']
            self.winning_line = data.get('winning_line')
            self.game_over = True
            self.draw_grid()
            self.status_label.config(text=f"Player {self.current_turn} wins!", fg="#ff6b6b")
            if self.winning_line:
                self.animate_winning_line(self.winning_line)
        elif data['type'] == 'draw':
            self.board = data.get('board', self.board)
            self.game_over = True
            self.draw_grid()
            self.status_label.config(text="It's a draw!", fg="#aaaaaa")
        elif data['type'] == 'reset':
            self.board = [["" for _ in range(3)] for _ in range(3)]
            self.current_turn = data.get('current_player', "X")
            self.game_over = False
            self.winning_line = None
            self.draw_grid()
            self.status_label.config(text=f"Player {self.current_turn}'s turn", fg="#f0f0f0")
        elif data['type'] == 'chat':
            sender = data.get('sender', '')
            message_text = data.get('message', '')
            is_you = sender == self.player_symbol
            self.append_chat_message(f"[{sender}] {message_text}", sent=is_you)

    def append_chat_message(self, message, sent=False):
        msg_frame = tk.Frame(self.chat_inner_frame, bg="#282c44")
        bubble = tk.Label(msg_frame, text=message, bg="#4a69bd" if sent else "#3a3f58",
                          fg="white", font=("Segoe UI", 11), wraplength=250,
                          justify="left", padx=10, pady=5)
        if sent:
            bubble.pack(anchor='e', padx=5, pady=2)
            msg_frame.pack(anchor='e', fill=tk.X, pady=2, padx=5)
        else:
            bubble.pack(anchor='w', padx=5, pady=2)
            msg_frame.pack(anchor='w', fill=tk.X, pady=2, padx=5)

        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1)

    def animate_winning_line(self, line):
        if not line:
            return

        offset = self.padding
        r1, c1 = line[0]
        r2, c2 = line[2]

        x1 = offset + c1 * self.cell_size + self.cell_size // 2
        y1 = offset + r1 * self.cell_size + self.cell_size // 2
        x2 = offset + c2 * self.cell_size + self.cell_size // 2
        y2 = offset + r2 * self.cell_size + self.cell_size // 2

        line_id = None
        steps = 20
        for i in range(steps + 1):
            if line_id:
                self.canvas.delete(line_id)
            nx = x1 + (x2 - x1) * i / steps
            ny = y1 + (y2 - y1) * i / steps
            line_id = self.canvas.create_line(x1, y1, nx, ny, fill="#feca57", width=8, capstyle="round")
            self.root.update()
            time.sleep(0.03)

if __name__ == "__main__":
    root = tk.Tk()
    client = AdvancedTicTacToeClient(root)
    root.mainloop()
