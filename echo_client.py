"""
sudo tcpdump -i lo -nn -XX
"""

import argparse
import socket
import time

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--host',
			type=str,
                        default='127.0.0.1',
			help='Host.')
    parser.add_argument('--port',
			type=int,
                        default=8001,
			help='Port.')
    parser.add_argument('--server_host',
			type=str,
                        default='127.0.0.1',
			help='Server host.')
    parser.add_argument('--server_port',
			type=int,
                        default=8000,
			help='Server port.')
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((args.host, args.port))
        s.connect((args.server_host, args.server_port))

        msg = b'PINGPING'
        s.sendall(msg)
        print(f'Sent {msg}.')

        msg = s.recv(1024)
        print(f'Received {msg}.')

if __name__ == '__main__':
    main()
