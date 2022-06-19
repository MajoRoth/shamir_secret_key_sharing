import pickle
import socket
import sys
import logging
from _thread import *

import settings
from member import Member
from utils import crypto

member = Member()
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
    global member
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

            if request_dict["request_code"] == "set_params":
                """
                    code 1
                    set_params
                    params t, n, a_coeff, points
                """
                try:
                    t = request_dict["request_args"]["t"]
                    n = request_dict["request_args"]["n"]
                    a_coeff = request_dict["request_args"]["a_coeff"]

                    # new inbal
                    encrypted_points = request_dict["request_args"]["points"]
                    real_points = pickle.loads(crypto.decrypt_message(encrypted_points, member.private_key))

                    member.set_parameters(t=t, n=n, a_coeff=a_coeff, points=real_points)
                    logging.info(f"Generated a Member successfully with t={t}, n={n}, a_coeff={a_coeff}, points={real_points}")
                    connection.sendall(pickle.dumps(settings.SUCCESS))

                except KeyError:
                    logging.error("Invalid parameters for \"request_code\"=1 - create dealer")
                    connection.sendall(pickle.dumps(settings.FAILURE))

            elif request_dict["request_code"] == "get_x":
                """
                    code 2
                    get my x 
                """
                x = member.get_my_x()
                logging.info(f"returned x value of points")
                connection.sendall(pickle.dumps({'code': 1, 'args': {'x': x}}))

            elif request_dict["request_code"] == "get_y_list":
                """
                    code 3
                    get my y list 
                """
                y_list = member.get_my_x()
                logging.info(f"returned y list value of points")
                connection.sendall(pickle.dumps({'code': 1, 'args': {'y_list': y_list}}))

            elif request_dict["request_code"] == "calc_cv":
                """
                    code 4
                    calculate cv
                    params x_arr, l
                """
                try:
                    x_arr = request_dict["request_args"]["t"]
                    l = request_dict["request_args"]["n"]
                    cv = member.calculate_cv(x_arr=x_arr, l=l)

                    logging.info(f"Calculated cv with l={l}, x_arr={x_arr}")

                    # new inbal
                    cv_str = pickle.dumps(cv)
                    cv_encrypted = crypto.encrypt_message(cv_str, VAL_PUB_KEY)
                    connection.sendall(pickle.dumps({'code': 1, 'args': {'cv': cv_encrypted}}))

                except KeyError:
                    logging.error("Invalid parameters for \"request_code\"=4 - calculate cv")
                    connection.sendall(pickle.dumps(settings.FAILURE))

            elif request_dict["request_code"] == "get_pk":
                """
                    code 5
                    get public key
                """
                pk = 1 # get publick key from member
                logging.info("returned publick key")
                connection.sendall(pickle.dumps({'code': 1, 'args': {'pk': pk}}))


            if request_dict["request_code"] == "init":
                """
                    code 6
                    create member with connection to the dealer
                    params dealer port and host
                """
                try:
                    host = request_dict["request_args"]["host"]
                    port = request_dict["request_args"]["port"]

                    DealerSocket = socket.socket()

                    logging.info('Waiting for connection')
                    try:
                        DealerSocket.connect((host, port))
                    except socket.error as e:
                        logging.error(str(e))

                    Response = DealerSocket.recv(settings.RECEIVE_BYTES)
                    d = {"request_code": "pop_points"}
                    DealerSocket.send(pickle.dumps(d))
                    Response = DealerSocket.recv(settings.RECEIVE_BYTES)

                    pickled_response = pickle.loads(Response)

                    # new inbal
                    encrypted_points = pickled_response["args"]["points"]
                    real_points = pickle.loads(crypto.decrypt_message(encrypted_points, member.private_key))

                    d = {"request_code": "gen_a_coeff"}
                    DealerSocket.send(pickle.dumps(d))
                    Response = DealerSocket.recv(settings.RECEIVE_BYTES)
                    pickled_response = pickle.loads(Response)
                    a_coeff = pickled_response["args"]["a_coeff"]

                    d = {"request_code": "get_t"}
                    DealerSocket.send(pickle.dumps(d))
                    Response = DealerSocket.recv(settings.RECEIVE_BYTES)
                    pickled_response = pickle.loads(Response)
                    t = pickled_response["args"]["t"]

                    d = {"request_code": "get_n"}
                    DealerSocket.send(pickle.dumps(d))
                    Response = DealerSocket.recv(settings.RECEIVE_BYTES)
                    pickled_response = pickle.loads(Response)
                    n = pickled_response["args"]["n"]

                    member.set_parameters(t=t, n=n, a_coeff=a_coeff, points=real_points)
                    logging.info(f"Generated a Member successfully with t={t}, n={n}, a_coeff={a_coeff}, points={real_points}")
                    connection.sendall(pickle.dumps(settings.SUCCESS))

                except KeyError:
                    logging.error("Invalid parameters for \"request_code\"=1 - create dealer")
                    connection.sendall(pickle.dumps(settings.FAILURE))

    connection.close()


if __name__ == "__main__":
    run(int(sys.argv[1]))
