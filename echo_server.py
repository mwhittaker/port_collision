import argparse
import socket


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--host',
			type=str,
                        default='127.0.0.1',
			help='Host.')
    parser.add_argument('--port',
			type=int,
                        default=8000,
			help='Port.')
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((args.host, args.port))
        s.listen()
        print(f'Server listening on {args.host}:{args.port}.')

        conn, addr = s.accept()
        print(f'Accepted {addr}')
        with conn:
            while True:
                msg = conn.recv(1024)
                if not msg:
                    break
                print(f'Received {msg}.')

                conn.sendall(msg)
                print(f'Sent {msg}.')


if __name__ == '__main__':
    main()
