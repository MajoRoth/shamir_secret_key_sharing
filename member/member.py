import numpy as np
import math
from numpy.polynomial.polynomial import Polynomial

import settings


class Member:

    def __init__(self, t: int, n: int, r: int, a_coeff: np.array, points: list):
        self.t = t
        self.n = n
        self.r = math.ceil((n - 1) / t)
        self.a_coeff = a_coeff
        self.points = points

    def get_my_x(self):
        return self.points[0][0]

    def get_my_y_list(self):
        return [p[1] for p in self.points]

    def calculate_cv(self, v: int, x_arr: list, l: int) -> float:
        """
        :param v: the index of this member in x_arr
        :param x_arr: arr of the members x-es
        :param l: the current threshold
        :return: the c value of this member
        """
        c_v = 0
        y_arr = self.get_my_y_list()
        x_v = x_arr[v]

        for i in range(self.r):
            value = self.a_coeff[i] * y_arr[i] % settings.p

            # calculate the product value
            prod = 1
            for j in range(l):
                if j != v:
                    prod *= (i+1-x_arr[j])/(x_v - x_arr[j]) % settings.p

            value *= prod % settings.p

            c_v += value % settings.p

        return c_v

    def __str__(self):
        return "member-> t={}, n={}, r={}, a_coeff={}, points={}".format(self.t, self.n, self.r, self.a_coeff, self.points)



def secret_reconstructor_for_changeable_threshold(p: int, l: int, members: list) -> float:
    """
    NEED TO BE MOVED
    :param p:
    :param l:
    :param members:
    :return:
    """
    x_arr = [s.points[0][0] for s in members]

    # calculate c value for each shareholder
    c_arr = [m.calculate_cv(v, x_arr, l) % p for v, m in enumerate(members)]

    # calculate the secret
    secret = sum(c_arr[:l]) % settings.p

    return secret


if __name__ == '__main__':
    t = 2  # t = num of functions
    l = 3  # threshold
    p = 100
    n = 3
    r = 2

    pols = [Polynomial([1, 1]), Polynomial([1, 2])]
    a_coeff = np.array([1, 2])  # len(a) = t

    members = [Member(p, t, n, r, a_coeff, 3, [pols[0](3), pols[1](3)]),
               Member(p, t, n, r, a_coeff, 4, [pols[0](4), pols[1](4)]),
               Member(p, t, n, r, a_coeff, 5, [pols[0](5), pols[1](5)])]

    s = secret_reconstructor_for_changeable_threshold(p, l, members)
    print(s)
