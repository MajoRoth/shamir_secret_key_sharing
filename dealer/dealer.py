import math
import settings
import random
from cryptography.hazmat.primitives import hashes
from utils import finite_field_helper as ffh
from utils import crypto
from utils.shamir import get_shares_no_secret, get_shares_no_secret_and_g_matrix, get_x_values, get_secret


class Dealer:
    """
        A class that implements a dealer
        calculates the polynoms and shares the points
    """

    def __init__(self, t, n, points_matrix=[], g_matrix=[], a_coeff=[], RSA=True):
        self.t = t
        self.n = n
        self.r = math.ceil((n - 1) / t)
        self.points_matrix = points_matrix  # matrix of dots [[(1,1), (2,2), ...], [(1,1), (2,2), ...]] each row stands for a polynom
        self.a_coeff = a_coeff
        self.g_matrix = g_matrix  # matrix of g**[hi coff] each row stands for a polynom
        self.pop_count = 0  # private
        self.secret = None
        self.hash = None
        if RSA:
            self.private_key, self.public_key = crypto.generate_keys()

        self.member_count = 0

    def get_g_matrix(self):
        return self.g_matrix

    def generate_polynomial_list_and_g_matrix(self):
        self.g_matrix = list()
        self.points_matrix = list()
        x_list = get_x_values(self.n)
        for i in range(self.r):
            shares, g_coff = get_shares_no_secret_and_g_matrix(self.t, self.n, x_list)
            self.points_matrix.append(shares)
            self.g_matrix.append(g_coff)

        return self.points_matrix, self.g_matrix

    def get_x_arr(self):  # call only after self.points_matrix has been populated
        return [point[0] for point in self.points_matrix[0]]

    def get_y_of_func_by_index(self, idx):
        return [y for (x, y) in self.points_matrix[idx]]

    def get_points_by_index(self, i):
        return [row[i] for row in self.points_matrix]

    def pop_points(self):
        if self.pop_count >= self.n:
            raise IndexError("All points were delivered")
        self.pop_count += 1
        return [row[self.pop_count - 1] for row in self.points_matrix]

    def generate_a_coeff_list(self):
        a_arr = []
        for i in range(self.r):
            a_arr.append(random.randrange(1, settings.p))
        self.a_coeff = a_arr

    def share_generation(self):
        # create h(i) vector
        h_i = [get_secret(poly_points[:self.t], i + 1) for i, poly_points in enumerate(self.points_matrix)]

        # get the secret
        secret = ffh.dot(self.a_coeff, h_i)
        self.secret = secret

        return secret

    def get_hash(self):
        self.share_generation()
        h = hashes.Hash(hashes.SHA256())
        h.update(bytes(self.secret))
        self.hash = h.finalize()
        self.secret = None
        return self.hash

    def get_n(self):
        return self.n

    def get_t(self):
        return self.t

    def get_index(self):
        count = self.member_count
        self.member_count += 1
        return count

    def __str__(self):
        return "dealer-> t={}, n={}, r={}, points={}, a_coeff={}, g_matrix={}".format(self.t, self.n, self.r,
                                                                                      self.points_matrix, self.a_coeff,
                                                                                      self.g_matrix)
