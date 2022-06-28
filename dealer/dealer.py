import math
import settings
import random
import numpy as np
from cryptography.hazmat.primitives import hashes

from utils import crypto
from utils.shamir import get_shares_no_secret, get_shares_no_secret_and_g_matrix, get_x_values, get_secret


class Dealer:
    """
        A class that implements a dealer
        calculates the polynoms and shares the points
    """

    def __init__(self, t, n, points_matrix=[], g_matrix=[], a_list=np.array([])):
        self.t = t
        self.n = n
        self.r = math.ceil((n - 1) / t)
        self.points_matrix = points_matrix  # matrix of dots [[(1,1), (2,2), ...], [(1,1), (2,2), ...]] each row stands for a polynom
        self.g_matrix= g_matrix #matrix of g**[hi coff] each row stands for a polynom
        self.a_list = a_list
        self.pop_count = 0  # private
        self.secret = None
        self.hash = None
        self.private_key, self.public_key = crypto.generate_keys()


    def generate_polynom_list(self):
        x_list = get_x_values(self.n)
        for i in range(self.r):
            self.points_matrix.append(get_shares_no_secret(self.t, self.n, x_list))
        return self.points_matrix

    def get_g_matrix(self):
        #todo:
        return self.g_matrix

    def generate_polynom_list_and_g_matrix(self):
        x_list = get_x_values(self.n)
        for i in range(self.r):
            shares, g_coff= get_shares_no_secret_and_g_matrix(self.t, self.n, x_list)
            self.points_matrix.append(shares)
            self.g_matrix.append(g_coff)
        return self.points_matrix,  self.g_matrix

    def get_x_arr(self):  # call only after self.points_matrix has been populated
        return [point[0] for point in self.points_matrix[0]]

    def get_y_of_func_by_index(self, idx):
        return [y for (x, y) in self.points_matrix[idx]]

    def get_points_by_index(self, i: object) -> object:
        return [row[i] for row in self.points_matrix]

    def pop_point(self):
        if self.pop_count >= self.n:
            raise IndexError("All points were delivered")
        self.pop_count += 1
        return [row[self.pop_count - 1] for row in self.points_matrix]

    def generate_a_coeff_list(self):
        a_arr = []
        for i in range(self.r):
            a_arr.append(random.randrange(1, settings.p))
        self.a_list = np.array(a_arr)
        return self.a_list

    def share_generation(self):
        # create h(i) vector
        h_i = np.array([get_secret(poly_points[:self.t], i + 1) for i, poly_points in enumerate(self.points_matrix)])

        # get the secret
        secret = self.a_list.dot(h_i) % settings.p
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

    def __str__(self):
        return "dealer-> t={}, n={}, r={}, points={}, a_coeff={}".format(self.t, self.n, self.r, self.points_matrix, self.g_matrix, self.a_list)


if __name__ == "__main__":
    d = Dealer(2, 5)
    print(d.generate_polynom_list())

    print(d.generate_polynom_list_and_g_coff())
    print(d.get_points_by_index(0))
    #assume we have list of points, g matrix and the process is:
    g=settings.g
    p=settings.p
    points_list=d.get_points_by_index(0)
    r=len(points_list)

    valid=True
    for i in range(r):
        point=points_list[i]
        commitment=g ** point[1] % p
        verification=0
        counter=0
        x_i=point[0]
        for j in g_coff[i]:"" # [g^a0, g^a1, g^a2, ..]
            verification+= j**(x_i**counter)
            counter+=1
        verification=verification %p
        print("for the" +str(i)+"point:")
        print("commitment="+str(commitment))
        print("verification=" + str(verification))
        if verification!=commitment:
            valid=False
    if valid=True:



    print("Share: f(" + str(i) + ") = " + str(f(i)))
    print("Commitment: g^f(" + str(i) + ") = " + str(g ** f(i) % p))
    print("Verification: (g^a0)*((g^a1)^i)*((g^a2)^(i^2)) = " + str(
        (g ** a0) * ((g ** a1) ** i) * ((g ** a2) ** (i ** 2)) % p) + "\n")


