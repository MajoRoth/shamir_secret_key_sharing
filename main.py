import numpy.polynomial
from scipy.interpolate import lagrange
import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial.polynomial import Polynomial

import member.member
import settings
import pickle
import validator.validator
from dealer.dealer import Dealer


if __name__ == '__main__':
    """
        https://numpy.org/doc/stable/reference/routines.polynomials.html
    """
    # x = np.array([0, 1, 2, 3])
    # y = x ** 3
    # poly = lagrange(x, y)
    # print(poly)
    # print(Polynomial(poly.coef[::-1]).coef)
    #
    # x_new = np.arange(0, 3.1, 0.1)
    # plt.scatter(x, y, label='data')
    # plt.plot(x_new, Polynomial(poly.coef[::-1])(x_new), label='Polynomial')
    # plt.plot(x_new, 3 * x_new ** 2 - 2 * x_new + 0 * x_new, label = r"$3 x^2 - 2 x$", linestyle = '-.')
    # plt.legend()
    # plt.show()

    # print([x for x in enumerate(range(0, 10))])
    # print(numpy.polynomial.polynomial.polyval([3], [1, 2, 3]))

    # tup_l = [(1, 2), (3, 4), (5, 6), (7, 8)]
    # print([t[0] for t in tup_l])
    # print([t[1] for t in tup_l])

    t = 2  # t = num of functions
    l = 2  # threshold
    p = 100
    n = 3
    r = 2

    d = Dealer(t=2, n=5)
    d.generate_a_coeff_list()
    d.generate_polynom_list()
    print(d)
    members = list()

    for i in range(3):
        members.append(member.member.Member(2, 5, d.a_list, d.pop_point()))
        print(members[i])

    points = [members[0].points, members[1].points]
    print(points)
    s = validator.validator.Validator.share_generation(points, np.array(d.a_list))
    print(s)

    # calc cv
    c_arr = [m.calculate_cv(d.get_x_arr(), l) % settings.p for v, m in enumerate(members)]
    print("c_arr = ", c_arr)

    print("key is: ", validator.validator.Validator.secret_reconstructor_for_changeable_threshold(l, c_arr))
    print(d.share_generation())

    # import socket
    #
    # DealerSocket = socket.socket()
    #
    # print('Waiting for connection')
    # try:
    #     DealerSocket.connect((settings.DEALER_HOST, settings.DEALER_PORT))
    # except socket.error as e:
    #     print(str(e))
    #
    # Response = DealerSocket.recv(settings.RECEIVE_BYTES)
    # print(Response)
    #
    # MemberSocket = socket.socket()
    #
    # print('Waiting for connection')
    # try:
    #     MemberSocket.connect((settings.MEMBER_HOST, settings.MEMBER_PORT))
    # except socket.error as e:
    #     print(str(e))
    #
    # Response = MemberSocket.recv(settings.RECEIVE_BYTES)
    # print(Response)
    #
    # d = {"request_code": 1, "request_args": {"t": 5, "n": 8}}
    # DealerSocket.send(pickle.dumps(d))
    # Response = DealerSocket.recv(settings.RECEIVE_BYTES)
    # print(pickle.loads(Response))
    #
    # d = {"request_code": 2}
    # DealerSocket.send(pickle.dumps(d))
    # Response = DealerSocket.recv(settings.RECEIVE_BYTES)
    # print(pickle.loads(Response))
    #
    # d = {"request_code": 4}
    # DealerSocket.send(pickle.dumps(d))
    # Response = DealerSocket.recv(settings.RECEIVE_BYTES)
    # print(pickle.loads(Response))
    #
    # d = {"request_code": 4}
    # DealerSocket.send(pickle.dumps(d))
    # Response = DealerSocket.recv(settings.RECEIVE_BYTES)
    # print(pickle.loads(Response))
    #
    # d = {"request_code": 4}
    # DealerSocket.send(pickle.dumps(d))
    # Response = DealerSocket.recv(settings.RECEIVE_BYTES)
    # print(pickle.loads(Response))
    #
    # d = {"request_code": 4}
    # DealerSocket.send(pickle.dumps(d))
    # Response = DealerSocket.recv(settings.RECEIVE_BYTES)
    # print(pickle.loads(Response))
    #
    # d = {"request_code": 4}
    # DealerSocket.send(pickle.dumps(d))
    # Response = DealerSocket.recv(settings.RECEIVE_BYTES)
    # print(pickle.loads(Response))
    #
    # d = {"request_code": 4}
    # DealerSocket.send(pickle.dumps(d))
    # Response = DealerSocket.recv(settings.RECEIVE_BYTES)
    # print(pickle.loads(Response))
    #
    # d = {"request_code": 4}
    # DealerSocket.send(pickle.dumps(d))
    # Response = DealerSocket.recv(settings.RECEIVE_BYTES)
    # points = pickle.loads(Response)
    # print(pickle.loads(Response))
    #
    # d = {"request_code": 5}
    # DealerSocket.send(pickle.dumps(d))
    # Response = DealerSocket.recv(settings.RECEIVE_BYTES)
    # a_coeff = pickle.loads(Response)
    # print(pickle.loads(Response))
    #
    # d = {"request_code": 1, "request_args": {
    #     "t": 5, "n": 8, "a_coeff": a_coeff, "points": points
    # }}
    # MemberSocket.send(pickle.dumps(d))
    # Response = MemberSocket.recv(settings.RECEIVE_BYTES)
    # print(pickle.loads(Response))
    #
    # d = {"request_code": 1, "request_args": {
    #     "t": 5, "n": 8, "a_coeff": a_coeff, "points": points
    # }}
    # MemberSocket.send(pickle.dumps(d))
    # Response = MemberSocket.recv(settings.RECEIVE_BYTES)
    # print(pickle.loads(Response))
    #
    #
    #
    #




