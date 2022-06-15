import numpy as np
import math

import settings


class Member:

    def __init__(self, t: int, n: int, a_coeff: np.array, x_share: int, ys_share: np.array):
        self.t = t
        self.n = n
        self.r = math.ceil((n - 1) / t)
        self.a_coeff = a_coeff
        self.points = [(x_share, y_share) for y_share in ys_share]

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
