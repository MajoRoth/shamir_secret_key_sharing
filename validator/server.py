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

    # -----------------------------------server functions--------------------------------------

    def start(self):
        self.start_connection_dealer()
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

                if request_dict["request_code"] == 'voting':
                    self.validate_secret(connection, request_dict)

        connection.close()

    def validate_secret(self, connection, request_dict):
        encrypted_cv_arr = request_dict["request_args"]["encrypted_cv_arr"]
        cv_arr = []
        for encrypted_cv in encrypted_cv_arr:
            curr_cv_str = crypto.decrypt_message(encrypted_cv, self.validator.private_key).decode()
            print("curr_cv_str: ", curr_cv_str)
            curr_cv = float(curr_cv_str)
            cv_arr.append(curr_cv)

        secret = self.validator.secret_reconstructor_for_changeable_threshold(cv_arr)
        res = self.validator.validate_secret(secret)
        logging.info(f"The result is: {res}")
        connection.sendall(pickle.dumps({"code": 1, "args": {"result": res}}))

    # -----------------------------------client functions--------------------------------------

    def start_connection_dealer(self):
        """
            send the validator details and get the public parameters
        """
        ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            ClientSocket.connect((settings.DEALER_HOST, settings.DEALER_PORT))
        except socket.error as e:
            logging.error(str(e))
        Response = ClientSocket.recv(settings.RECEIVE_BYTES)
        logging.info(Response)

        d = {"request_code": "start_connection",
             "request_args": {'ip': self.ip, 'port': self.port, 'pk': crypto.pub_key2str(self.validator.public_key)}}
        ClientSocket.send(pickle.dumps(d))
        Response = ClientSocket.recv(settings.RECEIVE_BYTES)
        pickled_response = pickle.loads(Response)

        if pickled_response['code'] == 0:
            logging.error(pickled_response['args']['message'])
            ClientSocket.close()
            return

        t = pickled_response['args']['t']
        a_coeff = pickled_response['args']['a_coeff']
        encrypted_hashed_secret = pickled_response['args']['hashed_secret']
        hashed_secret = crypto.decrypt_message(encrypted_hashed_secret, self.validator.private_key)
        self.validator.set_parameters(t, a_coeff, hashed_secret)

        logging.info('action succeeded - the validator and the dealer are connected! ')
        ClientSocket.close()


if __name__ == '__main__':
    validator_entity = ValidatorServer()
    validator_entity.start()

# todo finish the action of increasing the threshold
# todo remember to run the dealer first
