from member.member import Member
from utils.shamir import get_secret
import settings
import numpy as np

from numpy.polynomial.polynomial import Polynomial


class Validator:
    @staticmethod
    def secret_reconstructor_for_changeable_threshold(l: int, c_arr: list) -> float:
        """
        :param l:
        :param c_arr:
        :return:
        """
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
