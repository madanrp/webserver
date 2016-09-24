#!/usr/bin/python
import argparse
import errno
import os
import socket

SERVER_ADDRESS = '127.0.0.1', 8000
request = b"""\
GET /hello HTTP/1.1

"""

def main(num_clients, num_trials):
    print SERVER_ADDRESS
    children = []
    for i in range(num_clients):
        pid = os.fork()
        if pid == 0:
            for j in range(num_trials):
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(SERVER_ADDRESS)
                client.sendall(request)
                data = client.recv(1024)
                client.close()
            os._exit(0)
        else:
            children.append(pid)
    for child in children:
        pid, status = os.waitpid(child, 0)
        print pid, status


if __name__ == "__main__":
    parser = argparse.ArgumentParser("http server client")
    parser.add_argument("--num-clients", dest="num_clients", 
                            type=int, default=1, help="Number of clients")
    parser.add_argument("--num-trials", dest="num_trials", 
                            type=int, default=100, help="number of trials per client") 
    args = parser.parse_args()
    main(args.num_clients, args.num_trials)
