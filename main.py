import numpy.polynomial
from scipy.interpolate import lagrange
import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial.polynomial import Polynomial

import member.member
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
    l = 3  # threshold
    p = 100
    n = 3
    r = 2

    d = Dealer(2, 5)
    d.generate_a_coeff_list()
    print(d.generate_polynom_list())
    a_coeff = np.array([1, 2])
    members = list()

    for i in range(5):
        members.append(member.member.Member(2, 3, 2, a_coeff, d.pop_point()))
        print(members[i])

    points = [members[0].points, members[1].points]
    print(points)
    s = validator.validator.Validator.share_generation(points)
    print(s)


