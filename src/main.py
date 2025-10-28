# src/cli/main.py
import threading
from datetime import datetime
from src.room.manager import RoomManager
from src.transport.socket_handler import EncryptedHostSocket, EncryptedPeerSocket

from termcolor import colored

room_manager = RoomManager()

def format_message(peer_id, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    return f"[{timestamp}] {peer_id}: {message}"

def host_room():
    host_ip = input("Enter your IP to host (0.0.0.0 for all interfaces): ").strip() or "0.0.0.0"
    host_port = int(input("Enter port to listen on (default 12345): ") or 12345)
    expiry = int(input("Room duration in seconds (default 300): ") or 300)

    room = room_manager.create_room(host_ip, host_port, expiry)
    host_socket = EncryptedHostSocket(host_ip, host_port)
    room.host_socket = host_socket  # link socket for cleanup
    host_socket.start()

    print(colored(f"[CLI] Room created! Room ID: {room.room_id}", "green"))
    print(colored(f"[CLI] Waiting for peers... (expires in {expiry}s)", "yellow"))

    try:
        while room.active:
            msg = input()
            host_socket.send_to_all(format_message("HOST", msg))
    except KeyboardInterrupt:
        print(colored("[CLI] Stopping room...", "red"))
        host_socket.stop()
        room_manager.remove_room(room.room_id)

def join_room():
    host_ip = input("Enter host IP to connect: ").strip()
    host_port = int(input("Enter host port (default 12345): ") or 12345)

    peer_socket = EncryptedPeerSocket(host_ip, host_port)
    peer_socket.connect()

    try:
        while True:
            msg = input()
            peer_socket.send(format_message("ME", msg))
    except KeyboardInterrupt:
        print(colored("[CLI] Disconnecting...", "red"))
        peer_socket.close()

def main():
    print(colored("Welcome to Secure Terminal Messenger", "green"))
    print("1. Host a room")
    print("2. Join a room")
    choice = input("Select an option: ").strip()

    if choice == "1":
        host_room()
    elif choice == "2":
        join_room()
    else:
        print(colored("Invalid option. Exiting.", "red"))

if __name__ == "__main__":
    main()
