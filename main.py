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


def old_main():
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
    import random
    random.seed(12)

    first_threshold = 2  # t = num of functions
    new_threshold = 3  # threshold
    members_num = 5

    d = Dealer(t=first_threshold, n=members_num)
    d.generate_a_coeff_list()
    d.generate_polynom_list()
    x = d.get_x_arr()

    y1 = d.get_y_of_func_by_index(0)
    y2 = d.get_y_of_func_by_index(1)
    print(f"y1={y1}")
    print(f"y2={y2}\n")

    get_pol(x, y1, y2, first_threshold)
    print("The dealer is: ", d)

    members = list()
    for i in range(members_num):
        members.append(member.member.Member(first_threshold, members_num, d.a_list, d.pop_point()))
        print(f"member number {i} is: {members[i]}")

    points = [members[0].points, members[1].points]
    print("The validator points:", points)
    s = validator.validator.Validator.share_generation(points, np.array(d.a_list), first_threshold)
    print("The validator key with share_generation (A1): ", s)

    # calc cv for each member
    c_arr = [m.calculate_cv(d.get_x_arr(), new_threshold) for v, m in enumerate(members)]
    print("c_arr = ", c_arr)

    print("The validator key with secret_reconstructor_for_changeable_threshold (A2): ",
          validator.validator.Validator.secret_reconstructor_for_changeable_threshold(new_threshold,
                                                                                      c_arr[:new_threshold]))
    print("The key according to the dealer with share_generation (A1): ", d.share_generation())


def sock_main():
    import socket

    ClientSocket = socket.socket()

    print('Waiting for connection')
    try:
        ClientSocket.connect((settings.DEALER_HOST, settings.DEALER_PORT))
    except socket.error as e:
        print(str(e))

    Response = ClientSocket.recv(settings.RECEIVE_BYTES)

    d = {"request": "send", "param": {"p1": 5, "p2": 8}}
    ClientSocket.send(pickle.dumps(d))


def new_main():
    # todo i saw that when n is growing, the number of functions need to grow either. because r = n-1/t and we run over r functions
    first_threshold = 2  # t = num of functions
    new_threshold = 4  # threshold
    members_num = 5

    points_matrix = [[(3, 9), (4, 12), (5, 15), (6, 18), (7, 21)],
                     [(3, 13), (4, 17), (5, 21), (6, 25), (7, 29)]]

    a_list = np.array([1, 2])
    get_pol([3, 4, 5, 6, 7], [4, 5, 6, 7, 8], [7, 9, 11, 13, 15], first_threshold)
    d = Dealer(t=first_threshold, n=members_num, points_matrix=points_matrix, a_list=a_list)
    print("The dealer is: ", d)

    members = list()
    for i in range(members_num):
        members.append(member.member.Member(first_threshold, members_num, d.a_list, d.pop_point()))
        print(f"member number {i} is: {members[i]}")

    points = [members[0].points, members[1].points]
    print("The validator points:", points)
    s = validator.validator.Validator.share_generation(points, np.array(d.a_list), first_threshold)
    print("The validator key with share_generation (A1): ", s)

    # calc cv for each member
    c_arr = [m.calculate_cv(d.get_x_arr(), new_threshold) for v, m in enumerate(members[:new_threshold])]
    print("c_arr = ", c_arr)

    print("The validator key with secret_reconstructor_for_changeable_threshold (A2): ",
          validator.validator.Validator.secret_reconstructor_for_changeable_threshold(new_threshold, c_arr))
    print("The key according to the dealer with share_generation (A1): ", d.share_generation())


def new2_main():
    first_threshold = 2  # t = num of functions
    new_threshold = 2  # threshold
    members_num = 4

    points_matrix = [[(9, 2), (6, 3), (3, 4), (7, 10)],
                     [(9, 6), (6, 9), (3, 1), (7, 8)]]

    a_list = np.array([8, 5])

    d = Dealer(t=first_threshold, n=members_num, points_matrix=points_matrix, a_list=a_list)
    print("The dealer is: ", d)

    x = d.get_x_arr()
    y1 = d.get_y_of_func_by_index(0)
    y2 = d.get_y_of_func_by_index(1)
    print(f"y1={y1}")
    print(f"y2={y2}\n")

    get_pol(x, y1, y2, first_threshold)

    members = list()
    for i in range(members_num):
        members.append(member.member.Member(first_threshold, members_num, d.a_list, d.pop_point()))
        print(f"member number {i} is: {members[i]}")

    points = [m.points for m in members[:2]]

    print("The validator points:", points)
    s = validator.validator.Validator.share_generation(points, np.array(d.a_list), first_threshold)
    print("The validator key with share_generation (A1): ", s)

    # calc cv for each member
    c_arr = [m.calculate_cv(d.get_x_arr(), new_threshold) for v, m in enumerate(members[:new_threshold])]
    print("c_arr = ", c_arr)

    print("The validator key with secret_reconstructor_for_changeable_threshold (A2): ",
          validator.validator.Validator.secret_reconstructor_for_changeable_threshold(new_threshold, c_arr))
    print("The key according to the dealer with share_generation (A1): ", d.share_generation())


def new3_main():
    first_threshold = 2  # t = num of functions
    new_threshold = 2  # threshold
    members_num = 4

    points_matrix = [[(3, 52), (4, 67), (5, 82), (6, 97)],
                     [(3, 130), (4, 167), (5, 204), (6, 241)]]

    a_list = np.array([8, 5])

    d = Dealer(t=first_threshold, n=members_num, points_matrix=points_matrix, a_list=a_list)
    print("The dealer is: ", d)

    x = d.get_x_arr()
    y1 = d.get_y_of_func_by_index(0)
    y2 = d.get_y_of_func_by_index(1)
    print(f"y1={y1}")
    print(f"y2={y2}\n")

    get_pol(x, y1, y2, first_threshold)

    members = list()
    for i in range(members_num):
        members.append(member.member.Member(first_threshold, members_num, d.a_list, d.pop_point()))
        print(f"member number {i} is: {members[i]}")

    points = [m.points for m in members[:2]]

    print("The validator points:", points)
    s = validator.validator.Validator.share_generation(points, np.array(d.a_list), first_threshold)
    print("The validator key with share_generation (A1): ", s)

    # calc cv for each member
    c_arr = [m.calculate_cv(d.get_x_arr(), new_threshold) for v, m in enumerate(members[:new_threshold])]
    print("c_arr = ", c_arr)

    print("The validator key with secret_reconstructor_for_changeable_threshold (A2): ",
          validator.validator.Validator.secret_reconstructor_for_changeable_threshold(new_threshold, c_arr))
    print("The key according to the dealer with share_generation (A1): ", d.share_generation())


def get_pol(x, y1, y2, t):
    print('---------------------------------------------------------------------------------------------------------')
    curr_poly = lagrange(x[:t], y1[:t])
    print('h1 = ', Polynomial(curr_poly.coef[::-1]))
    curr_poly = lagrange(x[:t], y2[:t])
    print('h2 = ', Polynomial(curr_poly.coef[::-1]))
    print('---------------------------------------------------------------------------------------------------------\n')


if __name__ == '__main__':
    """
        https://numpy.org/doc/stable/reference/routines.polynomials.html
    """
    # old_main()
    # new2_main()
    # new_main()
    new3_main()