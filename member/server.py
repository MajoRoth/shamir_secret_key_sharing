import pickle
import socket
import sys
import logging
import threading
import time
from _thread import *
from threading import *
from member import Member
from utils import crypto
import settings

logging.basicConfig(level=settings.LOG_LEVEL)


class MemberServer:
    _lock = threading.RLock()

    def __init__(self, ip, port):
        self.member = Member()  # an empty member
        self.ip = ip
        self.port = port
        self.members_connection_details = []  # list of (ip, port)
        self.thread_count = 0
        self.validator_details = None
        self.voting_time = False
        self.votes_num = 0
        self.cv_votes = []
        self.have_to_answer = False
        self.client_thread = Thread(target=self.start_cli)
        self.server_thread = Thread(target=self.start_serv)
        self.pause = False
        self.pause_cond = threading.Condition(threading.Lock())

    def start(self):
        self.client_thread.start()
        time.sleep(1)
        self.server_thread.start()

    # -----------------------------------client functions--------------------------------------

    def start_cli(self):
        while True:
            with self.pause_cond:
                while self.pause:
                    self.pause_cond.wait()
                print(f"{settings.Colors.client}What do you want to do? (choose a number){settings.Colors.RESET}")
                print(f"{settings.Colors.client}[1] - Get data from dealer{settings.Colors.RESET}")
                print(f"{settings.Colors.client}[2] - Send a voting requests to others{settings.Colors.RESET}")
                print(f"{settings.Colors.client}[3] - Send a request to increase the threshold{settings.Colors.RESET}")
                print(f"{settings.Colors.client}[4] - check g_matrix{settings.Colors.RESET}")
                print(f"{settings.Colors.client}[other] - Refresh{settings.Colors.RESET}")
                res = input()
                logging.debug("Got input {}".format(res))
                if res == '1':
                    try:
                        self.dealer_sign_up()
                    except (ConnectionResetError, OSError, socket.error):
                        logging.error('dealer is closed')
                elif res == '2':
                    msg = input("Why you need the key?")
                    self.voting_request(msg)
                elif res == '3':
                    msg = input("Enter the new threshold: ")
                    try:
                        new_threshold = int(msg)
                    except ValueError:
                        logging.error("the new threshold must be an integer!")
                    self.increase_threshold_request(new_threshold)
                elif res == '4':
                    self.compare_g_matrix()

    def dealer_sign_up(self, host=settings.DEALER_HOST, port=settings.DEALER_PORT):
        ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect to the dealer
        ClientSocket.connect((host, port))
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

        self.member.index = pickled_response["args"]["index"]
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

        # get the g_matrix from the dealer
        d = {"request_code": "get_g_matrix"}
        ClientSocket.send(pickle.dumps(d))
        Response = ClientSocket.recv(settings.RECEIVE_BYTES)
        pickled_response = pickle.loads(Response)
        if pickled_response['code'] == 0:
            logging.error(pickled_response['args']['message'])
            ClientSocket.close()
            return
        g_matrix = pickled_response["args"]["g_matrix"]

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
        self.member.set_parameters(t=t, n=n, a_coeff=a_coeff, x_arr=x_arr, points=real_points, g_matrix=g_matrix)
        logging.info(f"Generated a Member successfully with t={t}, n={n}, a_coeff={a_coeff}, "
                     f"points={real_points}, g_matrix={g_matrix}")
        ClientSocket.close()

        # verify the dealer points with feldman's algorithm
        res = self.member.verify_my_points()
        logging.info("result of checking the dealer with feldman's algorithm: " + str(res))

    def voting_request(self, msg):
        if self.member.is_empty():
            logging.error('you are not registered')
            return

        if len(self.members_connection_details) == 0:
            logging.error('your members details list is empty')
            return

        if len(self.members_connection_details) < self.member.n - 1:
            logging.error('not all members connected')
            return

        self.voting_time = True

        # connect to each member and send him the voting request
        for (host, port, _) in self.members_connection_details:
            ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ClientSocket.connect((host, port))

            Response = ClientSocket.recv(settings.RECEIVE_BYTES)
            logging.info(Response)

            # get vote from member. we send our details in order to be identified
            d = {"request_code": "voting_request", "request_args": {"ip": self.ip, "port": self.port,
                                                                    "pk": crypto.pub_key2str(self.member.public_key),
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

    def increase_threshold_request(self, new_threshold):
        if self.member.is_empty():
            logging.error('you are not registered')
            return

        if len(self.members_connection_details) == 0:
            logging.error('your members details list is empty')
            return

        # check the threshold value
        if new_threshold > self.member.n or new_threshold < self.member.current_l:
            logging.error(
                "the new threshold must be smaller or equal than n and bigger or equal then the last threshold!")
            return

        if len(self.members_connection_details) < self.member.n - 1:
            logging.error('not all members connected')
            return

        if self.member.is_empty():
            logging.error("The member didn't connect to the dealer")
            return

        for (host, port, _) in self.members_connection_details:
            ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ClientSocket.connect((host, port))

            Response = ClientSocket.recv(settings.RECEIVE_BYTES)
            logging.info(Response)

            d = {"request_code": "increase_threshold", "request_args": {"new_threshold": new_threshold}}
            ClientSocket.send(pickle.dumps(d))
            ClientSocket.close()
            self.member.current_l = new_threshold

    def compare_g_matrix(self):
        if self.member.is_empty():
            logging.error('you are not registered')
            return

        if len(self.members_connection_details) == 0:
            logging.error('your members details list is empty')
            return

        if len(self.members_connection_details) < self.member.n - 1:
            logging.error('not all members connected')
            return

        # connect to each member and send him the get_g_matrix request
        for (host, port, _) in self.members_connection_details:
            ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ClientSocket.connect((host, port))

            Response = ClientSocket.recv(settings.RECEIVE_BYTES)
            logging.info(Response)

            # get vote from member. we send our details in order to be identified
            d = {"request_code": "get_g_matrix"}
            ClientSocket.send(pickle.dumps(d))
            Response = ClientSocket.recv(settings.RECEIVE_BYTES)
            pickled_response = pickle.loads(Response)
            if pickled_response['code'] == 0:
                logging.error(pickled_response['args']['message'])
                ClientSocket.close()
                return
            g_matrix = pickled_response["args"]["g_matrix"]

            if g_matrix == self.member.g_matrix:
                logging.info(f"g_matrix was verified with the member: {host}:{port}")
            else:
                logging.info(f"your g_matrix is different matrix from the matrix of the member: {host}:{port}")

            ClientSocket.close()

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
            try:
                data = connection.recv(settings.RECEIVE_BYTES)
            except ConnectionResetError:
                # connection.close()
                break

            if data:
                request_dict = pickle.loads(data)
                # logging.debug(f"{request_dict}")

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
                elif request_dict["request_code"] == "increase_threshold":
                    self.increase_threshold(connection, request_dict)
                elif request_dict["request_code"] == "get_g_matrix":
                    self.send_g_matrix(connection, request_dict)

        connection.close()

    def get_members_details(self, connection, request_dict):
        members_list = request_dict["request_args"]["members_list"]
        self.validator_details = (request_dict["request_args"]["validator_ip"],
                                  request_dict["request_args"]["validator_port"],
                                  crypto.str2pub_key(request_dict["request_args"]["validator_pk"]))
        self.members_connection_details = [(ip, port, crypto.str2pub_key(pk_str)) for (ip, port, pk_str) in
                                           members_list]

        # delete myself from the list
        for (ip, port, pk) in self.members_connection_details:
            if crypto.pub_key2str(pk) == crypto.pub_key2str(self.member.public_key):
                self.members_connection_details.remove((ip, port, pk))

        logging.info("got members_connection_details")
        connection.send(pickle.dumps(settings.SUCCESS))

        cv = self.member.calculate_cv()
        self.cv_votes = [crypto.encrypt_message(str(cv).encode(), self.validator_details[2])]

    def voting(self, connection, request_dict):
        self.pause = True
        self.pause_cond.acquire()

        ip = request_dict["request_args"]["ip"]
        port = request_dict["request_args"]["port"]
        pk_str = request_dict["request_args"]["pk"]
        msg = request_dict["request_args"]["req_msg"]

        result = input(f"{settings.Colors.server}member ip:{ip}, port:{port} wants to get the key. "
                       f"\nHis reason is: {msg}. Do you want to vote? [y/n]{settings.Colors.RESET}")
        logging.info('my vote: {}'.format(result))

        self.pause = False
        self.pause_cond.notify()
        self.pause_cond.release()

        ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect to the member
        try:
            ClientSocket.connect((ip, port))
        except socket.error as e:
            logging.error(str(e))
        Response = ClientSocket.recv(settings.RECEIVE_BYTES)
        logging.info(Response)

        # send vote


        if result == 'y':
            # send to the member the cv encrypted by the validator public key
            cv = self.member.calculate_cv()
            encrypted_cv = crypto.encrypt_message(str(cv).encode(), self.validator_details[2])
            ClientSocket.sendall(pickle.dumps({'request_code': 'after_voting', 'request_args': {'vote': 'y',
                                                                                                'cv': encrypted_cv}}))
            logging.debug("sent Cv")
        else:
            ClientSocket.sendall(
                pickle.dumps({'request_code': 'after_voting', 'request_args': {'vote': 'n', 'cv': None}}))
            ClientSocket.close()
            return

        #


        ClientSocket.close()

    def wait_for_votes(self, connection, request_dict):
        vote = request_dict["request_args"]["vote"]
        self.votes_num += 1

        if self.voting_time:
            if vote == 'y':
                encrypted_cv = request_dict["request_args"]["cv"]
                self.cv_votes.append(encrypted_cv)

                logging.info("got vote - yes:)")
            else:
                logging.info("got vote - no:(")

            if len(self.cv_votes) == self.member.current_l:
                logging.info("voting is over!")
                self.validate_cv_list(self.cv_votes)
                cv = self.member.calculate_cv()
                self.cv_votes = [crypto.encrypt_message(str(cv).encode(), self.validator_details[2])]
                self.votes_num = 0
                self.voting_time = False

            elif self.votes_num == self.member.n - 1:
                logging.info("voting is over!")
                cv = self.member.calculate_cv()
                self.cv_votes = [crypto.encrypt_message(str(cv).encode(), self.validator_details[2])]
                self.votes_num = 0
                self.voting_time = False

        else:
            self.votes_num = 0
            self.voting_time = False
            cv = self.member.calculate_cv()
            self.cv_votes = [crypto.encrypt_message(str(cv).encode(), self.validator_details[2])]
            logging.error("voting is over!")

    def increase_threshold(self, connection, request_dict):
        new_threshold = request_dict["request_args"]["new_threshold"]

        self.member.current_l = new_threshold
        logging.info("threshold changed... -> new_threshold: " + str(new_threshold))

    def send_g_matrix(self, connection, request_dict):
        connection.sendall(pickle.dumps({'code': 1, 'args': {'g_matrix': self.member.g_matrix}}))
        logging.debug("sent g_matrix")


if __name__ == "__main__":
    member_entity = MemberServer(settings.DEALER_HOST, int(sys.argv[1]))
    member_entity.start()
