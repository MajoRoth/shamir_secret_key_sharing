import math
import settings
import random
from cryptography.hazmat.primitives import hashes
from utils import finite_field_helper as ffh
from utils import crypto
from utils.shamir import get_shares_no_secret_and_g_matrix, get_x_values, get_secret


class Dealer:
    """
        A class that implements a dealer
        calculates the polynomials and shares the points
    """

    def __init__(self, t, n, points_matrix=[], g_matrix=[], a_coeff=[], RSA=True):
        """
        initialize dealer object

        :param t: initial threshold
        :param n: number of members
        :param points_matrix: matrix of the members points. each row stands for a polynomial
        :param g_matrix: matrix of g in power the polynomials coefficients. each row stands for a polynomial
        :param a_coeff: coefficients array
        """
        self.t = t
        self.n = n
        self.r = math.ceil((n - 1) / t)
        self.points_matrix = points_matrix  # e.g: [[(1,1), (2,2), ...], [(1,1), (2,2), ...]]
        self.a_coeff = a_coeff
        self.g_matrix = g_matrix  # matrix of g**[hi coff]
        self.pop_count = 0  # private
        self.secret = None
        self.hash = None
        if RSA:
            self.private_key, self.public_key = crypto.generate_keys()

    def get_g_matrix(self):
        """
        returns the g_matrix of the dealer
        :return: matrix of g in power the polynomials coefficients
        """
        return self.g_matrix

    def generate_polynomial_list_and_g_matrix(self):
        """
        generates list of polynomials and calculate g_matrix
        :return: matrix of the members points and matrix of g in power the polynomials coefficients
        """
        self.g_matrix = list()
        self.points_matrix = list()
        x_list = get_x_values(self.n)

        # for each polynomial
        for i in range(self.r):
            shares, g_coff = get_shares_no_secret_and_g_matrix(self.t, self.n, x_list)
            self.points_matrix.append(shares)
            self.g_matrix.append(g_coff)

        return self.points_matrix, self.g_matrix

    def get_x_arr(self):
        """
        returns an array of the x values of each member points
        Note: this function called only after self.points_matrix has been populated
        :return: the x values of each member points
        """
        return [point[0] for point in self.points_matrix[0]]

    def get_y_of_func_by_index(self, idx):
        """
        returns the y values of specific polynomial
        :param idx: the index of the wanted polynomial
        :return: array of y values
        """
        return [y for (x, y) in self.points_matrix[idx]]

    def get_points_by_index(self, i):
        """
        returns points of specific polynomial
        :param i: the index of the wanted polynomial
        :return: array of points
        """
        return [row[i] for row in self.points_matrix]

    def pop_points(self):
        """
        pop points for a member (one point from each polynomial)
        :return: array of points
        """
        if self.pop_count >= self.n:
            raise IndexError("All points were delivered")
        self.pop_count += 1
        return [row[self.pop_count - 1] for row in self.points_matrix]

    def generate_a_coeff_list(self):
        """
        generates coefficients array
        """
        a_arr = []
        for i in range(self.r):
            a_arr.append(random.randrange(1, settings.p))
        self.a_coeff = a_arr

    def share_generation(self):
        """
        calculate the secret using the first algorithm (A1 - page 4) from the article:
        https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=9246739
        :return: the secret
        """
        # create h(i) vector
        h_i = [get_secret(poly_points[:self.t], i + 1) for i, poly_points in enumerate(self.points_matrix)]

        # get the secret
        secret = ffh.dot(self.a_coeff, h_i)
        self.secret = secret
        print("secret: ", secret)
        return secret

    def get_hash(self):
        """
        :return: hash of the secret
        """
        self.share_generation()
        h = hashes.Hash(hashes.SHA256())
        h.update(bytes(self.secret))
        self.hash = h.finalize()
        self.secret = None
        return self.hash

    def get_n(self):
        """
        :return: members amount
        """
        return self.n

    def get_t(self):
        """
        :return: initial threshold
        """
        return self.t

    def __str__(self):
        return "dealer-> t={}, n={}, r={}, points={}, a_coeff={}, g_matrix={}".format(self.t, self.n, self.r,
                                                                                      self.points_matrix, self.a_coeff,
                                                                                      self.g_matrix)
