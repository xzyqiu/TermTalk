import threading
import argparse
import sys
from datetime import datetime
from src.room.manager import RoomManager
from src.transport.socket_handler import EncryptedHostSocket, EncryptedPeerSocket
from src.transport.tor_proxy import set_tor_enabled, is_tor_enabled
from termcolor import colored

room_manager = RoomManager()


def format_message(peer_id: str, message: str) -> str:
    timestamp = datetime.now().strftime("%H:%M:%S")
    return f"[{timestamp}] {peer_id}: {message}"


def host_room() -> None:
    print(colored("[SECURITY] Default binding is localhost (127.0.0.1) - only accessible from this machine", "yellow"))
    print(colored("[WARNING] Use 0.0.0.0 to bind all interfaces (exposes to network/internet)", "red"))
    host_ip = input("Enter your IP to host (default 127.0.0.1): ").strip() or "127.0.0.1"
    host_port = int(input("Enter port to listen on (default 12345): ") or 12345)
    expiry = int(input("Room duration in seconds (default 300): ") or 300)

    room = room_manager.create_room(host_ip, host_port, expiry)
    host_socket = EncryptedHostSocket(host_ip, host_port)
    room.host_socket = host_socket  # link socket for cleanup
    host_socket.start()

    print(colored(f"[CLI] Room created! Room ID: {room.room_id}", "green"))
    print(colored(f"[CLI] Waiting for peers... (expires in {expiry}s)", "yellow"))
    print(colored("Peers should join by entering the Room ID (not your IP).", "cyan"))

    try:
        while room.active:
            msg = input()
            host_socket.send_to_all(format_message("HOST", msg))
    except KeyboardInterrupt:
        print(colored("[CLI] Stopping room...", "red"))
        host_socket.stop()
        room_manager.remove_room(room.room_id)


def join_room() -> None:
    room_id = input("Enter Room ID to join: ").strip()
    room = room_manager.get_room(room_id)
    if room is None:
        print(colored(f"[CLI] Room '{room_id}' not found or expired.", "red"))
        return

    host_ip = room.host_ip
    host_port = room.host_port

    peer_socket = EncryptedPeerSocket(host_ip, host_port)
    try:
        peer_socket.connect()
    except Exception as e:
        print(colored(f"[CLI] Failed to connect to host: {e}", "red"))
        return

    try:
        while True:
            msg = input()
            peer_socket.send(format_message("ME", msg))
    except KeyboardInterrupt:
        print(colored("[CLI] Disconnecting...", "red"))
        peer_socket.close()


def main() -> None:
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="TermTalk - Secure peer-to-peer terminal chat",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 main.py              # Normal mode
  python3 main.py --tor        # Route through Tor (requires Tor running)
  python3 -m src.main --tor    # Alternative invocation
"""
    )
    parser.add_argument(
        '--tor',
        action='store_true',
        help='Route connections through Tor SOCKS5 proxy (127.0.0.1:9050)'
    )
    parser.add_argument(
        '--tor-port',
        type=int,
        default=9050,
        help='Tor SOCKS5 proxy port (default: 9050)'
    )
    
    args = parser.parse_args()
    
    # Privacy protection check
    from src.utils.privacy import get_privacy_info
    privacy_status = get_privacy_info()
    
    # Enable Tor if requested
    if args.tor:
        set_tor_enabled(True, args.tor_port)
        print(colored("[TOR] Tor mode enabled - connections will route through SOCKS5 proxy", "cyan"))
        print(colored(f"[TOR] Using Tor proxy at 127.0.0.1:{args.tor_port}", "cyan"))
        print(colored("[TOR] Make sure Tor is running (e.g., systemctl start tor)", "yellow"))
    
    print(colored("Welcome to TermTalk", "green"))
    
    # Display privacy status
    if privacy_status["uses_ephemeral_ids"]:
        print(colored("🔒 Privacy: Ephemeral IDs only (no MAC, hostname, or system info exposed)", "cyan"))
    
    if is_tor_enabled():
        print(colored("🧅 Tor Mode Active", "magenta"))
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
