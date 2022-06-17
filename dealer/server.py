import pickle
import socket
import sys
import logging
from _thread import *

import settings
from dealer import Dealer

dealer = None
logging.basicConfig(level=logging.DEBUG)


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

            if request_dict["request_code"] == 1:
                """
                    code 1
                    create dealer
                    params t, n
                """
                try:
                    t = request_dict["request_args"]["t"]
                    n = request_dict["request_args"]["n"]
                    dealer = Dealer(t=t, n=n)
                    logging.info(f"Generated a Dealer successfully with t={t} and n={n}")
                    connection.sendall(settings.SUCCESS)

                except KeyError:
                    logging.error("Invalid parameters for \"request_code\"=1 - create dealer")
                    connection.sendall(settings.FAILURE)



            elif request_dict["request_code"] == 2:
                """
                    code 2
                    generate polynoms list
                """
                dealer.generate_polynom_list()
                logging.info(f"Generate polynoms list successfully")
                connection.sendall(settings.SUCCESS)

            elif request_dict["request_code"] == 3:
                """
                    code 3
                    get x list
                """
                x_list = dealer.generate_polynom_list()
                logging.info(f"Returned x list successfully")
                connection.sendall({'code': 1, 'args': {'x_list': x_list}})



            #
            # if re.findall("^create_entity ", data):


    connection.close()


if __name__ == "__main__":
    run(int(sys.argv[1]))
