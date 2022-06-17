import pickle
import socket
import sys
import logging
from _thread import *

import settings
from member import Member

member = None
logging.basicConfig(level=settings.LOG_LEVEL)


def run(PORT):
    ServerSocket = socket.socket()
    ThreadCount = 0
    try:
        ServerSocket.bind((settings.DEALER_HOST, PORT))
    except socket.error as e:
        logging.error(e)

    ServerSocket.listen(5)

    while True:
        Client, address = ServerSocket.accept()
        logging.info("connected to {}:{}".format(address[0], address[1]))
        start_new_thread(threaded_client, (Client,))
        ThreadCount += 1
        logging.info("thread number {}".format(ThreadCount))

    ServerSocket.close()


def threaded_client(connection):
    global dealer
    connection.send(str.encode('Welcome to the Server'))
    while True:
        data = connection.recv(settings.RECEIVE_BYTES)

        if data:
            request_dict = pickle.loads(data)
            logging.debug(f"{request_dict}")

            try:
                request_dict["request_code"]
            except KeyError:
                logging.error("A key \"request_code\" does not exist")
                break

            if True:
                pass # ...


    connection.close()


if __name__ == "__main__":
    run(int(sys.argv[1]))
