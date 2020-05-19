"""
When you `connect` a client socket without expliticly choosing a port, the
operating system chooses a port for you. These ports are called _ephemeral
ports_ and are typically in the range of say 32,000-ish to 60,000-ish.

With such a large number of ephemeral ports, I thought it would be rare to have
muliple clients assigned the same ephemeral port. However, I found that clients
which open a lot of sockets do end up with port collisions relatively often. I
realized that this is the birthday paradox in action.

The number of sockets we need to expect a collision half the time is roughly
the square root of the number of available ports. If we have 30,000 ports, then
with about 175 sockets, we expect a collision roughly half the time. You can
use this script to verify this yourself.

This also taught me that you can have two separate client sockets with the same
local address and port and that's totally fine. A socket is actually identified
by a 5-tuple of the protocol (e.g., TPC), the local address, the local port,
the remote address, and the remote port. I didn't know that, but in hindsight
it seems obvious. For example, every socket created by a server socket `accept`
has the same local address and port (but different remote address and port).
"""

import argparse
import collections
import socket
import sys
import threading
import time


port_counts = collections.Counter()
port_counts_lock = threading.Lock()


def server(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        _, (_, client_port) = s.accept()
        with port_counts_lock:
            port_counts[client_port] += 1


def client(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))


def main() -> None:
    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_port',
			type=int,
                        default=8000,
			help='Starting port.')
    parser.add_argument('--num_ports',
			type=int,
                        default=200,
			help='Number of ports to try.')
    args = parser.parse_args()
    assert(args.num_ports > 0)
    assert(args.num_ports < 256)

    # Start servers. Note that we have to vary the address. If we don't, the OS
    # assigns increasing port numbers which makes it pretty much impossible to
    # have a collision.
    servers = [
        threading.Thread(target=server,
                         args=(f'127.0.0.{i + 1}', args.start_port + i))
        for i in range(0, args.num_ports)
    ]
    for s in servers:
        s.start()

    # Wait for servers to start up.
    time.sleep(1)

    # Start clients.
    clients = [
        threading.Thread(target=client,
                         args=(f'127.0.0.{i + 1}', args.start_port + i))
        for i in range(0, args.num_ports)
    ]
    for c in clients:
        c.start()

    # Wait for servers and clients.
    for thread in servers + clients:
        thread.join()

    # Report collisions.
    collision_found = False
    for (port, frequency) in port_counts.items():
        if (frequency > 1):
            collision_found = True
            print(f'Port {port} assigned {frequency} times.')

    if not collision_found:
        print('No collision found.')


if __name__ == '__main__':
    main()
