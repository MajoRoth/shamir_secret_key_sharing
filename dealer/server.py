import pickle
import socket
import sys
import logging
from _thread import *

import settings
from dealer import Dealer
from utils import crypto

logging.basicConfig(level=settings.LOG_LEVEL)


class DealerServer:
    def __init__(self, ip, port, t, n):
        self.dealer = Dealer(t=t, n=n)
        self.dealer.generate_polynomial_list()
        self.ip = ip
        self.port = port
        self.members_connection_details = []
        self.thread_count = 0
        self.validator_details = None

    def start(self):
        self.get_validator_details()
        ServerSocket = socket.socket()

        try:
            ServerSocket.bind((self.ip, self.port))
        except socket.error as e:
            logging.error(e)

        ServerSocket.listen(5)
        logging.info("dealer server is listening...")

        while True:
            client, address = ServerSocket.accept()
            logging.info("connected to {}:{}".format(address[0], address[1]))
            start_new_thread(self.threaded_client, (client,))
            self.thread_count += 1
            logging.info("thread number {}".format(self.thread_count))

        ServerSocket.close()

    def threaded_client(self, connection):
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

                if request_dict["request_code"] == "get_x_list":
                    """
                        code 3
                        get x list
                    """
                    x_list = self.dealer.generate_polynomial_list()
                    logging.info(f"Returned x list successfully")
                    connection.sendall(pickle.dumps({'code': 1, 'args': {'x_list': x_list}}))

                elif request_dict["request_code"] == "pop_points":
                    self.pop_points(connection, request_dict)

                elif request_dict["request_code"] == "send_details":
                    self.save_member_details(connection, request_dict)

                elif request_dict["request_code"] == "gen_a_coeff":
                    self.get_a_coeff(connection)

                elif request_dict["request_code"] == "get_hash":
                    self.get_hash(connection)

                elif request_dict["request_code"] == "get_pk":
                    self.get_public_key(connection)

                elif request_dict["request_code"] == "get_n":
                    self.get_n(connection)

                elif request_dict["request_code"] == "get_t":
                    self.get_t(connection)

                elif request_dict["request_code"] == "get_x_arr":
                    self.get_x_arr(connection)

        connection.close()

    def pop_points(self, connection, request_dict):
        """
            code 4
            pop point
            params: pk
        """
        try:
            pk = request_dict["request_args"]["pk"]

            if pk in [member_pk for (member_ip, member_port, member_pk) in self.members_connection_details]:
                raise Exception("This member already exists")

            real_points = self.dealer.pop_points()

            points_str = pickle.dumps(real_points)
            encrypted_points = crypto.encrypt_message(points_str, crypto.str2pub_key(pk))

            logging.info(f"Popped points successfully")
            connection.sendall(pickle.dumps({'code': 1, 'args': {'points': encrypted_points}}))

        except Exception as e:
            logging.error(f"Error: {e}")
            connection.sendall(pickle.dumps({'code': 0, 'args': {'message': e}}))

    def save_member_details(self, connection, request_dict):
        """
        send_details
        params ip, port, pk
        """
        if len(self.members_connection_details) >= self.dealer.get_n():
            raise Exception("We already have all members")

        member_pk = request_dict["request_args"]["pk"]
        member_ip = request_dict["request_args"]["ip"]
        member_port = request_dict["request_args"]["port"]

        if (member_ip, member_port, member_pk) in self.members_connection_details:
            logging.error(f"This member already exists")
            connection.sendall(pickle.dumps({'code': 0}))

        self.members_connection_details.append((member_ip, member_port, member_pk))

        logging.info(f"Saved member successfully")
        connection.sendall(pickle.dumps({'code': 1}))

        if len(self.members_connection_details) == self.dealer.n:
            self.send_details()

    def get_a_coeff(self, connection):
        """
            code 5
            generate a_coeff list
        """
        a_coeff = self.dealer.generate_a_coeff_list()
        logging.info(f"Generated a_coeff list successfully")
        connection.sendall(pickle.dumps({'code': 1, 'args': {'a_coeff': a_coeff}}))

    def get_hash(self, connection):
        """
            code 6
            get hash
        """
        hash = self.dealer.get_hash()
        logging.info(f"Generated hash successfully")
        connection.sendall(pickle.dumps({'code': 1, 'args': {'hash': hash}}))

    def get_public_key(self, connection):
        """
            code 7
            get public key
        """
        logging.info("returned public key")
        connection.sendall(pickle.dumps({'code': 1, 'args': {'pk': self.dealer.public_key}}))

    def get_n(self, connection):
        logging.info("returned n")
        connection.sendall(pickle.dumps({'code': 1, 'args': {'n': self.dealer.get_n()}}))

    def get_t(self, connection):
        logging.info("returned t")
        connection.sendall(pickle.dumps({'code': 1, 'args': {'t': self.dealer.get_t()}}))

    def get_x_arr(self, connection):
        x_arr = self.dealer.get_x_arr()
        logging.info(f"returned x_arr")
        connection.sendall(pickle.dumps({'code': 1, 'args': {'x_arr': x_arr}}))

    # -----------------------------------client functions--------------------------------------

    def send_details(self):
        for member_ip, member_port, member_pk in self.members_connection_details:
            ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                ClientSocket.connect((member_ip, member_port))
            except socket.error as e:
                logging.error(str(e))
            Response = ClientSocket.recv(settings.RECEIVE_BYTES)
            logging.info(Response)

            d = {"request_code": "send_details", "request_args": {"members_list": self.members_connection_details,
                                                                  "validator_details": self.validator_details}}
            ClientSocket.send(pickle.dumps(d))
            Response = ClientSocket.recv(settings.RECEIVE_BYTES)
            pickled_response = pickle.loads(Response)
            if pickled_response['code'] == 0:
                logging.error(pickled_response['args']['message'])
                ClientSocket.close()
                return
            logging.info('action succeeded')

    def get_validator_details(self):
        ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            ClientSocket.connect((settings.VALIDATOR_HOST, settings.VALIDATOR_PORT))
        except socket.error as e:
            logging.error(str(e))
        Response = ClientSocket.recv(settings.RECEIVE_BYTES)
        logging.info(Response)

        d = {"request_code": "get_details"}
        ClientSocket.send(pickle.dumps(d))
        Response = ClientSocket.recv(settings.RECEIVE_BYTES)
        pickled_response = pickle.loads(Response)
        if pickled_response['code'] == 0:
            logging.error(pickled_response['args']['message'])
            ClientSocket.close()
            return
        self.validator_details = settings.VALIDATOR_HOST, settings.VALIDATOR_PORT, pickled_response['args']['pk']
        logging.info('action succeeded')
        ClientSocket.close()

if __name__ == "__main__":
    dealer_entity = DealerServer(settings.DEALER_HOST, port=settings.DEALER_PORT, t=int(sys.argv[1]), n=int(sys.argv[2]))
    dealer_entity.start()
