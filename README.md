# Distributed Tic Tac Toe Game with Chat

This is a Python-based two-player Tic Tac Toe game implemented using a client-server architecture with socket programming. It includes a feature-rich GUI on the client side using `tkinter`, and real-time chat functionality between players. The game is designed as a distributed system and requires two clients to connect to a single server.

---

## 🔧 Features

* 🎮 Interactive 3x3 Tic Tac Toe game for two players
* 🧠 Server-enforced turn-based logic with win/draw detection
* 💬 Real-time in-game chat between players
* ♻️ Game reset functionality
* ✨ GUI with animated winning line
* ⚡ Built using Python `socket`, `threading`, `tkinter`, and `json` libraries

---

## 🗂️ Project Structure

```
.
├── server.py        # Server-side code
└── client.py        # Client-side GUI application
```

---

## 🧰 Requirements

* Python 3.x
* Tkinter (comes pre-installed with most Python distributions)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/junaid17-zx/distributed-tic-tac-toe.git
cd distributed-tic-tac-toe
```

### 2. Run the Server

On one computer (or terminal window):

```bash
python server.py
```

You’ll see:

```
Server started. Waiting for connections...
```

### 3. Run the Client (on two separate machines or terminals)

On each client computer:

```bash
python client.py
```

Make sure both clients are connected to the same network and can access the server. Adjust the IP address in the `AdvancedTicTacToeClient` initialization if needed:

```python
client = AdvancedTicTacToeClient(root, host='SERVER_IP', port=12345)
```

---

## 🕹️ How to Play

* Players are assigned "X" or "O" upon connection.
* Players take turns clicking on the 3x3 grid to place their symbol.
* The game announces the winner or draw.
* Players can reset the game using the **Reset Game** button.
* Use the chat box on the right to send real-time messages.

---

## 👥 Team Members (Example)

* Junaid Ahmad
* Ibrar Ahmad
---

## 🛠️ Technical Notes

* Communication between server and clients is done using JSON messages.
* Server logic controls game flow and validates moves.
* Clients render GUI and respond to game state updates.
* Server can handle only **two clients at a time**.

---

## 📌 Future Improvements

* Add support for more games or spectators
* Persist chat and match history
* Implement authentication and player profiles
* Containerize the project using Docker for deployment

---

## 📃 License

This project is for educational use. Feel free to fork and modify it!

