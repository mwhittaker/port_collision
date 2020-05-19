import argparse
import socket
import threading
import time


def server(args) -> None:
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


def client(args) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((args.host, args.port))
        s.connect((args.remote_host, args.remote_port))

        while True:
            msg = b'PINGPING'
            s.sendall(msg)
            print(f'Sent {msg}.')

            msg = s.recv(1024)
            print(f'Received {msg}.')

            time.sleep(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--host',
			type=str,
                        default='127.0.0.1',
			help='Host.')
    parser.add_argument('--port',
			type=int,
                        required=True,
			help='Port.')
    parser.add_argument('--remote_host',
			type=str,
                        default='127.0.0.1',
			help='Remote host.')
    parser.add_argument('--remote_port',
			type=int,
                        required=True,
			help='Remote port.')
    parser.add_argument('--delay',
			type=int,
                        default=5,
			help='Delay (in seconds) to start client.')
    args = parser.parse_args()

    s = threading.Thread(target=server, args=(args,))
    c = threading.Thread(target=client, args=(args,))
    s.start()
    time.sleep(args.delay)
    c.start()
    s.join()
    c.join()


if __name__ == '__main__':
    main()
