import pickle
import socket
import sys
import logging
from _thread import *
from threading import *
import time
import settings
from utils import crypto
from validator import Validator

logging.basicConfig(level=settings.LOG_LEVEL)


class ValidatorServer:
    def __init__(self, ip=settings.VALIDATOR_HOST, port=settings.VALIDATOR_PORT):
        self.ip = ip
        self.port = port
        self.validator = Validator()
        self.thread_count = 0

    def start(self):
        ServerSocket = socket.socket()

        try:
            ServerSocket.bind((self.ip, self.port))
        except socket.error as e:
            logging.error(e)

        ServerSocket.listen(5)

        while True:
            Client, address = ServerSocket.accept()
            logging.info("connected to {}:{}".format(address[0], address[1]))
            start_new_thread(self.threaded_client, (Client,))
            self.thread_count += 1
            logging.info("thread number {}".format(self.thread_count))

        ServerSocket.close()

    def threaded_client(self, connection):
        connection.send(b'Welcome to the Server')

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

                if request_dict["request_code"] == 'get_details':
                    """
                        code 1
                        secret_reconstructor_for_changeable_threshold
                        params l, c_arr
                    """
                    self.send_pk(connection)

                elif request_dict["request_code"] == 'voting':
                    self.validate_secret(connection, request_dict)

        connection.close()

    def send_pk(self, connection):
        # send ip, port and public key to the dealer

        logging.info("return public key")
        connection.sendall(pickle.dumps({'code': 1, 'args': {'pk': self.validator.public_key}}))

    def validate_secret(self, connection, request_dict):
        points_matrix_encrypted = request_dict["request_args"]["points_matrix"]

        # new inbal
        points_matrix_str = crypto.decrypt_message(points_matrix_encrypted, self.validator.private_key)
        points_matrix = pickle.loads(points_matrix_str)

        a_coeff = request_dict["request_args"]["a_coeff"]
        t = request_dict["request_args"]["t"]
        s = Validator.share_generation(points_matrix=points_matrix, a_coeff=a_coeff, t=t)
        logging.info(
            f"Generated a Dealer successfully with points_matrix={points_matrix} and a_coeff={a_coeff}")
        connection.sendall(pickle.dumps({"code": 1, "args": {"secret": s}}))

    def get_details_list(self):
        pass

if __name__ == '__main__':
    validator_entity = ValidatorServer()


# todo finish the connection to the validator from his side
# finish the action of increasing the threshold