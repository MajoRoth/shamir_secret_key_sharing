import pickle
import socket
import sys
import logging
import time
from _thread import *
from threading import *
from member import Member
from utils import crypto
import settings

logging.basicConfig(level=settings.LOG_LEVEL)


class MemberServer:
    def __init__(self, ip, port):
        self.member = Member()  # an empty member
        self.ip = ip
        self.port = port
        self.members_connection_details = []  # list of (ip, port)
        self.thread_count = 0
        self.validator_details = None
        self.voting_time = False
        self.cv_votes = []

    def start(self):
        Thread(target=self.start_cli).start()
        time.sleep(1)
        Thread(target=self.start_serv).start()

    # -----------------------------------client functions--------------------------------------

    def start_cli(self):
        while True:
            print(f"{settings.Colors.client}what do you want to do? (choose a number){settings.Colors.RESET}")
            print(f"{settings.Colors.client}[1] - get data from dealer{settings.Colors.RESET}")
            print(f"{settings.Colors.client}[2] - send a voting requests to others{settings.Colors.RESET}")
            print(f"{settings.Colors.client}[3] - send a request to increase the threshold{settings.Colors.RESET}")
            print(f"{settings.Colors.client}[other] - stay in the menu{settings.Colors.RESET}")
            res = input()
            if res == '1':
                self.dealer_sign_up()
            elif res == '2':
                msg = input("why you need the key?")
                self.voting_request(msg)
            elif res == '3':
                msg = input("why do you want to increase the threshold?")
                self.increase_threshold_request(msg)

    def dealer_sign_up(self, host=settings.DEALER_HOST, port=settings.DEALER_PORT):
        ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect to the dealer
        try:
            ClientSocket.connect((host, port))
        except socket.error as e:
            logging.error(str(e))
        Response = ClientSocket.recv(settings.RECEIVE_BYTES)
        logging.info(Response)

        # get points from the dealer
        d = {"request_code": "pop_points", "request_args": {"pk": crypto.pub_key2str(self.member.public_key)}}
        ClientSocket.send(pickle.dumps(d))
        Response = ClientSocket.recv(settings.RECEIVE_BYTES)
        pickled_response = pickle.loads(Response)
        if pickled_response['code'] == 0:
            logging.error(pickled_response['args']['message'])
            ClientSocket.close()
            return
        encrypted_points = pickled_response["args"]["points"]
        real_points = pickle.loads(crypto.decrypt_message(encrypted_points, self.member.private_key))

        # get a_coeff arr from the dealer
        d = {"request_code": "gen_a_coeff"}
        ClientSocket.send(pickle.dumps(d))
        Response = ClientSocket.recv(settings.RECEIVE_BYTES)
        pickled_response = pickle.loads(Response)
        if pickled_response['code'] == 0:
            logging.error(pickled_response['args']['message'])
            ClientSocket.close()
            return
        a_coeff = pickled_response["args"]["a_coeff"]

        # get x_arr from the dealer
        d = {"request_code": "get_x_arr"}
        ClientSocket.send(pickle.dumps(d))
        Response = ClientSocket.recv(settings.RECEIVE_BYTES)
        pickled_response = pickle.loads(Response)
        if pickled_response['code'] == 0:
            logging.error(pickled_response['args']['message'])
            ClientSocket.close()
            return
        x_arr = pickled_response["args"]["x_arr"]

        # get the t parameter from the dealer
        d = {"request_code": "get_t"}
        ClientSocket.send(pickle.dumps(d))
        Response = ClientSocket.recv(settings.RECEIVE_BYTES)
        pickled_response = pickle.loads(Response)
        if pickled_response['code'] == 0:
            logging.error(pickled_response['args']['message'])
            ClientSocket.close()
            return
        t = pickled_response["args"]["t"]

        # get the n parameter from the dealer
        d = {"request_code": "get_n"}
        ClientSocket.send(pickle.dumps(d))
        Response = ClientSocket.recv(settings.RECEIVE_BYTES)
        pickled_response = pickle.loads(Response)
        if pickled_response['code'] == 0:
            logging.error(pickled_response['args']['message'])
            ClientSocket.close()
            return
        n = pickled_response["args"]["n"]

        # send ip, port and public key to the dealer
        d = {"request_code": "send_details", "request_args": {"ip": self.ip, "port": self.port,
                                                              "pk": crypto.pub_key2str(self.member.public_key)}}
        ClientSocket.send(pickle.dumps(d))
        Response = ClientSocket.recv(settings.RECEIVE_BYTES)
        pickled_response = pickle.loads(Response)
        if pickled_response['code'] == 0:
            logging.error(pickled_response['args']['message'])
            ClientSocket.close()
            return

        # save the parameters in the member variable
        self.member.set_parameters(t=t, n=n, a_coeff=a_coeff, x_arr=x_arr, points=real_points)
        logging.info(f"Generated a Member successfully with t={t}, n={n}, a_coeff={a_coeff}, points={real_points}")
        ClientSocket.close()

    def voting_request(self, msg):
        if self.member.is_empty():
            logging.error('you are not registered')
            return

        if len(self.members_connection_details) < self.member.n:
            logging.error('not all members connected')
            return

        ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.voting_time = True
        no_count = 0
        encrypted_cv_arr = []

        # connect to each member and send him the voting request
        for (host, port) in self.members_connection_details:
            try:
                ClientSocket.connect((host, port))
            except socket.error as e:
                logging.error(str(e))
            Response = ClientSocket.recv(settings.RECEIVE_BYTES)
            logging.info(Response)

            # get vote from member
            d = {"request_code": "voting_request", "request_args": {"ip": self.ip, "port": self.port,
                                                                    "pk": self.member.public_key,
                                                                    "req_msg": msg}}
            ClientSocket.send(pickle.dumps(d))

        ClientSocket.close()

    def validate_cv_list(self, encrypted_cv_arr):
        host, port, _ = self.validator_details
        ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect to the validator
        try:
            ClientSocket.connect((host, port))
        except socket.error as e:
            logging.error(str(e))
        Response = ClientSocket.recv(settings.RECEIVE_BYTES)
        logging.info(Response)

        # send encrypted_cv_arr
        d = {"request_code": "voting", "request_args": {"encrypted_cv_arr": encrypted_cv_arr}}
        ClientSocket.send(pickle.dumps(d))
        Response = ClientSocket.recv(settings.RECEIVE_BYTES)
        pickled_response = pickle.loads(Response)
        if pickled_response['code'] == 0:
            logging.error(pickled_response['args']['message'])
            ClientSocket.close()
            return

        result = pickled_response["args"]["result"]

        if result is True:
            print(f"{settings.Colors.client}Your suggestion was accepted and verified!!!!!!{settings.Colors.RESET}")
        else:
            print(f"{settings.Colors.client}Your suggestion was not accepted and verified:({settings.Colors.RESET}")

        ClientSocket.close()

    def increase_threshold_request(self, msg):
        # TODO
        ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            if self.member.is_empty():
                raise Exception("The member didn't connect to the dealer")
            pass
        except KeyError:
            logging.error("Invalid parameters for \"request_code\"=2 - increase_threshold_request")
            ClientSocket.sendall(pickle.dumps(settings.FAILURE))
        pass

    # -----------------------------------server functions--------------------------------------

    def start_serv(self):
        ServerSocket = socket.socket()

        try:
            ServerSocket.bind((self.ip, self.port))
        except socket.error as e:
            logging.error(e)

        ServerSocket.listen(5)

        while True:
            client, address = ServerSocket.accept()
            logging.info("connected to {}:{}".format(address[0], address[1]))
            start_new_thread(self.threaded_client, (client,))
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

                if request_dict["request_code"] == "send_details":
                    self.get_members_details(connection, request_dict)
                elif request_dict["request_code"] == "voting_request":
                    self.voting(connection, request_dict)
                elif request_dict["request_code"] == "after_voting":
                    self.wait_for_votes(connection, request_dict)
                elif request_dict["request_code"] == "get_pk":  # API
                    pk = 1  # get public key from member
                    logging.info("returned publick key")
                    connection.sendall(pickle.dumps({'code': 1, 'args': {'pk': pk}}))

        connection.close()

    def get_members_details(self, connection, request_dict):
        members_list = request_dict["request_args"]["members_list"]
        self.validator_details = request_dict["request_args"]["validator_details"]
        self.members_connection_details = members_list

        # delete myself from the list
        self.members_connection_details.remove((self.ip, self.port, self.member.public_key))

        logging.info("got members_connection_details")
        connection.send(pickle.dumps(settings.SUCCESS))

    def voting(self, connection, request_dict):
        connection.send(settings.SUCCESS)

        ip = request_dict["request_args"]["ip"]
        port = request_dict["request_args"]["port"]
        pk = request_dict["request_args"]["pk"]
        msg = request_dict["request_args"]["req_msg"]
        res = input(f"{settings.Colors.client}member ip:{ip}, port:{port}, public key:{pk} want to get the key. "
                    f"his reason is: {msg}. do you want to vote? [y/n]{settings.Colors.RESET}")

        ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connect to the member
        try:
            ClientSocket.connect((ip, port))
        except socket.error as e:
            logging.error(str(e))
        Response = ClientSocket.recv(settings.RECEIVE_BYTES)
        logging.info(Response)

        # send vote
        if res == 'y':
            # send to the member the cv encrypted by the validator public key
            cv = self.member.calculate_cv()
            encrypted_cv = crypto.encrypt_message(str(cv).encode(), self.validator_details[2])
            ClientSocket.sendall(pickle.dumps({'request_code': 'after_voting', 'request_args': {'vote': 'y',
                                                                                                'cv': encrypted_cv}}))
        else:
            ClientSocket.sendall(pickle.dumps({'request_code': 'after_voting', 'args': {'vote': 'n', 'cv': None}}))

        ClientSocket.close()

    def wait_for_votes(self, connection, request_dict):
        vote = request_dict["request_args"]["vote"]
        if self.voting_time:
            if vote == 'y':
                encrypted_cv = request_dict["request_args"]["cv"]
                self.cv_votes.append(encrypted_cv)

                logging.info("got vote - yes:)")

                if len(self.cv_votes) == self.member.current_l:
                    self.validate_cv_list(self.cv_votes)
                    self.cv_votes = []
                    self.voting_time = False
            else:
                logging.info("got vote - no:(")
        else:
            logging.error("this member doesn't wait for votes")
        connection.send(pickle.dumps(settings.SUCCESS))



if __name__ == "__main__":
    member_entity = MemberServer(settings.DEALER_HOST, int(sys.argv[1]))
    member_entity.start()
