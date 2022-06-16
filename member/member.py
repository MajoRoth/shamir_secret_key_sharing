import numpy as np
import math
from numpy.polynomial.polynomial import Polynomial

import settings


class Member:

    def __init__(self, t: int, n: int, a_coeff: np.array, points: list):
        self.t = t
        self.n = n
        self.r = math.ceil((n - 1) / t)
        self.a_coeff = a_coeff
        self.points = points
        self.current_l = t
        self.cv = None

    def get_my_x(self):
        return self.points[0][0]

    def get_my_y_list(self):
        return [p[1] for p in self.points]

    def calculate_cv(self, x_arr: list, l: int) -> float:
        """
        :param x_arr: arr of the members x-es
        :param l: the current threshold
        :return: the c value of this member
        """
        c_v = 0
        y_arr = self.get_my_y_list()
        x_v = self.get_my_x()

        for i in range(self.r):
            value = self.a_coeff[i] * y_arr[i] % settings.p

            # calculate the product value
            prod = 1
            for j in range(l):
                if x_arr[j] != x_v:
                    prod *= (i+1-x_arr[j])/(x_v - x_arr[j]) % settings.p

            value *= prod % settings.p

            c_v += value % settings.p

        self.cv = c_v
        return c_v

    def increase_threshold(self):
        pass

    def __str__(self):
        return "member-> t={}, n={}, r={}, a_coeff={}, points={}".format(self.t, self.n, self.r, self.a_coeff, self.points)
