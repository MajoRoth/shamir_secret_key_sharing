import settings
import numpy as np
from member.member import Member
from shamir.tcss import *

import math
from numpy.polynomial.polynomial import Polynomial


class Validator:
    @staticmethod
    def secret_reconstructor_for_changeable_threshold(l: int, members: list) -> float:
        """
        Need to get only a list of Cv from the mebers and return the sum mod P.
        :param l:
        :param members:
        :return:
        """
        x_arr = [s.points[0][0] for s in members]

        # calculate c value for each shareholder
        c_arr = [m.calculate_cv(v, x_arr, l) % settings.p for v, m in enumerate(members)]

        # calculate the secret
        secret = sum(c_arr[:l]) % settings.p

        return secret

    @staticmethod
    def share_generation(points_matrix: list, a_coeff: np.array) -> int:
        """
        :param points_matrix: matrix of points, each row is the points of a member
        :param a_coeff: the public a_coeff published by the dealer
        :return: the secret
        """
        # TODO check number of points
        points_matrix_T = list(map(list, zip(*points_matrix)))

        # create h(i) vector
        h_i = np.array([get_secret(poly_points, i+1) for i, poly_points in enumerate(points_matrix_T)])

        print("h_i = ", h_i)
        print("a_coeff = ", a_coeff)

        # get the secret
        secret = a_coeff.dot(h_i) % settings.p

        return secret


if __name__ == '__main__':
    t = 2  # (t - 1) = the polynomial order => t = num of polynomials
    l = 3  # threshold
    p = 100
    n = 5

    pols = [Polynomial([1, 1]), Polynomial([1, 2])]
    a_coeff = np.array([1, 2])  # len(a) = t

    members = [Member(t, n, a_coeff, 3, [pols[0](3), pols[1](3)]),
               Member(t, n, a_coeff, 4, [pols[0](4), pols[1](4)]),
               Member(t, n, a_coeff, 5, [pols[0](5), pols[1](5)])]

    s = Validator.secret_reconstructor_for_changeable_threshold(l, members)
    print(s)
