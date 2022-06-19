import pickle
import socket
import sys
import logging
from _thread import *

import settings
from validator import Validator

logging.basicConfig(level=settings.LOG_LEVEL)


def run(PORT):
    ServerSocket = socket.socket()
    ThreadCount = 0
    try:
        ServerSocket.bind((settings.VALIDATOR_HOST, settings.VALIDATOR_PORT))
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
                    secret_reconstructor_for_changeable_threshold
                    params l, c_arr
                """
                try:
                    l = request_dict["request_args"]["l"]
                    c_arr = request_dict["request_args"]["c_arr"]
                    s = Validator.secret_reconstructor_for_changeable_threshold(l, c_arr)
                    logging.info(f"Generated a Dealer successfully with l={l} and c_arr={c_arr}")
                    connection.sendall(pickle.dumps({"code": 1, "args": {"secret": s}}))

                except KeyError:
                    logging.error("Invalid parameters for \"request_code\"=1 - secret_reconstructor_for_changeable_threshold")
                    connection.sendall(pickle.dumps(settings.FAILURE))

            elif request_dict["request_code"] == 2:
                """
                    code 2
                    share_generation
                    params points_matrix, a_coeff
                """
                try:
                    points_matrix = request_dict["request_args"]["points_matrix"]
                    a_coeff = request_dict["request_args"]["a_coeff"]
                    s = Validator.share_generation(points_matrix=points_matrix, a_coeff=a_coeff)
                    logging.info(f"Generated a Dealer successfully with points_matrix={points_matrix} and a_coeff={a_coeff}")
                    connection.sendall(pickle.dumps({"code": 1, "args": {"secret": s}}))

                except KeyError:
                    logging.error("Invalid parameters for \"request_code\"=1 - secret_reconstructor_for_changeable_threshold")
                    connection.sendall(pickle.dumps(settings.FAILURE))


            elif request_dict["request_code"] == 3:
                """
                    code 3
                    validate secret
                    params secret, hash
                """
                try:
                    secret = request_dict["request_args"]["secret"]
                    h = request_dict["request_args"]["hash"]
                    res = Validator.validate_secret(secret, h)
                    if res:
                        logging.info(f"Secret has been validated successfully")
                        connection.sendall(pickle.dumps(settings.SUCCESS))
                    else:
                        logging.warning(f"Secret is not valid")
                        connection.sendall(pickle.dumps(settings.FAILURE))

                except KeyError:
                    logging.error("Invalid parameters for \"request_code\"=1 - secret_reconstructor_for_changeable_threshold")
                    connection.sendall(pickle.dumps(settings.FAILURE))



    connection.close()


if __name__ == "__main__":
    run(int(sys.argv[1]))
