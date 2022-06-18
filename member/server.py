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


            if request_dict["request_code"] == 1:
                """
                    code 1
                    create member
                    params t, n
                """
                try:
                    t = request_dict["request_args"]["t"]
                    n = request_dict["request_args"]["n"]
                    a_coeff = request_dict["request_args"]["a_coeff"]
                    points = request_dict["request_args"]["points"]
                    member = Member(t=t, n=n, a_coeff=a_coeff, points=points)
                    logging.info(f"Generated a Member successfully with t={t}, n={n}, a_coeff={a_coeff}, points={points}")
                    connection.sendall(settings.SUCCESS)

                except KeyError:
                    logging.error("Invalid parameters for \"request_code\"=1 - create dealer")
                    connection.sendall(settings.FAILURE)


            elif request_dict["request_code"] == 2:
                """
                    code 2
                    get my x 
                """
                x = member.get_my_x()
                logging.info(f"returned x value of points")
                connection.sendall({'code': 1, 'args': {'x': x}})

            elif request_dict["request_code"] == 3:
                """
                    code 3
                    get my y list 
                """
                y_list = member.get_my_x()
                logging.info(f"returned y list value of points")
                connection.sendall({'code': 1, 'args': {'y_list': y_list}})

            elif request_dict["request_code"] == 4:
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
                    connection.sendall({'code': 1, 'args': {'cv': cv}})

                except KeyError:
                    logging.error("Invalid parameters for \"request_code\"=4 - calculate cv")
                    connection.sendall(settings.FAILURE)



    connection.close()


if __name__ == "__main__":
    run(int(sys.argv[1]))
