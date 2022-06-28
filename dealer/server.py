import pickle
import socket
import sys
import logging
from _thread import *

import settings
from dealer import Dealer
from utils import crypto

dealer = None
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

            if request_dict["request_code"] == "create_dealer":
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
                    connection.sendall(pickle.dumps(settings.SUCCESS))

                except KeyError:
                    logging.error("Invalid parameters for \"request_code\"=1 - create dealer")
                    connection.sendall(pickle.dumps(settings.FAILURE))

            elif request_dict["request_code"] == "gen_poly_list":
                """
                    code 2
                    generate polynoms list
                """
                points = dealer.generate_polynom_list()
                logging.info(f"Generate polynoms list successfully")
                logging.debug(f"{points}")
                connection.sendall(pickle.dumps(settings.SUCCESS))

            elif request_dict["request_code"] == "gen_poly_list_and_g_coff":
                """
                    code 2
                    generate polynoms list
                """
                points, g_coff = dealer.generate_polynom_list_and_g_coff()
                logging.info(f"Generate polynoms list successfully")
                logging.debug(f"{points}")
                connection.sendall(pickle.dumps(settings.SUCCESS))

            elif request_dict["request_code"] == "get_x_list":
                """
                    code 3
                    get x list
                """
                x_list = dealer.generate_polynom_list()
                logging.info(f"Returned x list successfully")
                connection.sendall(pickle.dumps({'code': 1, 'args': {'x_list': x_list}}))

            elif request_dict["request_code"] == "pop_points":
                """
                    code 4
                    pop point
                    params: pk
                """
                try:
                    real_points = dealer.pop_point()

                    # new inbal
                    points_str = pickle.dumps(real_points)
                    pk = request_dict["request_args"]["pk"]
                    encrypted_points = crypto.encrypt_message(points_str, crypto.str2pub_key(pk))

                    logging.info(f"Popped points successfully")
                    connection.sendall(pickle.dumps({'code': 1, 'args': {'points': encrypted_points}}))
                except IndexError:
                    logging.error(f"All points were delivered")
                    connection.sendall(pickle.dumps({'code': 0}))

            elif request_dict["request_code"] == "gen_a_coeff":
                """
                    code 5
                    generate a_coeff list
                """
                a_coeff = dealer.generate_a_coeff_list()
                logging.info(f"Generated a_coeff list successfully")
                connection.sendall(pickle.dumps({'code': 1, 'args': {'a_coeff': a_coeff}}))

            elif request_dict["request_code"] == "get_hash":
                """
                    code 6
                    get hash
                """
                hash = dealer.get_hash()
                logging.info(f"Generated hash successfully")
                connection.sendall(pickle.dumps({'code': 1, 'args': {'hash': hash}}))

            elif request_dict["request_code"] == "get_pk":
                """
                    code 7
                    get public key
                """
                pk = 1 # get publick key from dealer
                logging.info("returned public key")
                connection.sendall(pickle.dumps({'code': 1, 'args': {'pk': pk}}))

            elif request_dict["request_code"] == "get_n":
                """
                    code 7
                    get public key
                """
                logging.info("returned n")
                connection.sendall(pickle.dumps({'code': 1, 'args': {'n': dealer.get_n()}}))

            elif request_dict["request_code"] == "get_t":
                """
                    code 7
                    get public key
                """
                logging.info("returned t")
                connection.sendall(pickle.dumps({'code': 1, 'args': {'t': dealer.get_t()}}))

    connection.close()


if __name__ == "__main__":
    run(int(sys.argv[1]))
