from utils import crypto
from utils.shamir import get_secret
import settings
import numpy as np
from cryptography.hazmat.primitives import hashes


class Validator:
    def __init__(self):
        self.private_key, self.public_key = crypto.generate_keys()
        self.t = None
        self.a_coeff = None
        self.hashed_secret = None

    def set_parameters(self, t: int, a_coeff: np.array, hashed_secret):
        self.t = t
        self.a_coeff = a_coeff
        self.hashed_secret = hashed_secret

    @staticmethod
    def secret_reconstructor_for_changeable_threshold(c_arr: list) -> float:
        """
        :param c_arr: cv values of each member
        :return:
        """
        l = len(c_arr)

        # calculate the secret
        secret = sum(c_arr[:l]) % settings.p

        return secret

    # todo delete it
    # @staticmethod
    # def share_generation(points_matrix: list, a_coeff: np.array) -> int:
    #     """
    #     :param points_matrix: matrix of points, each row is the points of a member
    #     :param a_coeff: the public a_coeff published by the dealer
    #     :return: the secret
    #     """
    #     # TODO check number of points
    #     points_matrix_T = list(map(list, zip(*points_matrix)))  # transpose on list of lists -> each row is function points
    #
    #     # create h(i) vector -> the y value of each function in x=i+1
    #     h_i = np.array([get_secret(poly_points, i+1) for i, poly_points in enumerate(points_matrix_T)])
    #
    #     print(f"h_i = {list(h_i)}, a_coeff = {a_coeff}")
    #
    #     # get the secret
    #     secret = a_coeff.dot(h_i) % settings.p
    #     return secret

    def validate_secret(self, secret):
        s = round(secret)
        h = hashes.Hash(hashes.SHA256())
        h.update(bytes(s))
        return h.finalize() == self.hashed_secret





