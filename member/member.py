import numpy as np
import math
from utils import crypto

import settings


class Member:
    def __init__(self):
        self.private_key, self.public_key = crypto.generate_keys()
        self.t = None
        self.n = None
        self.r = None
        self.a_coeff = None
        self.points = None
        self.g_coff = None
        self.current_l = None
        self.cv = None

    def set_parameters(self, t: int, n: int, a_coeff: np.array, points: list = None, g_coff: list = None):
        self.t = t
        self.n = n
        self.r = math.ceil((n - 1) / t)
        self.a_coeff = a_coeff
        self.points = points
        self.current_l = t
        self.cv = None
        self.private_key, self.public_key = crypto.generate_keys()
        self.g_coff = g_coff

    def get_my_x(self):
        return self.points[0][0]

    def get_my_y_list(self):
        return [p[1] for p in self.points]

    def verify_my_points(self, g_matrix):
        # given my g_matrix check if the
        g_matrix = g_matrix
        ans = True
        x = self.get_my_x()
        x_pow = []
        t = self.t
        for i in range(t):
            x_pow.append(x ** i)
        x_pow.reverse()
        i = 0
        for p in self.points:
            g_y = settings.g ** p[1]
            g_coff = g_matrix[i]
            verify = 1
            for i in range(t):
                verify *= g_coff[i] ** x_pow[i]
            if verify != g_y:
                ans=False
                break
            i+=1
        return ans

    def calculate_cv(self, x_arr: list, l: int) -> float:
        """
        :param x_arr: arr of the members x-es
        :param l: the current threshold
        :return: the c value of this member
        """

        c_v = 0
        y_arr = self.get_my_y_list()
        x_v = self.get_my_x()
        print(f"\nx_arr={x_arr}")

        for i in range(self.r):
            print(f"ai={self.a_coeff[i]}, hi[xwv]={y_arr[i]}, xwv={x_v}, i={i + 1}")
            value = self.a_coeff[i] * y_arr[i]

            # calculate the product value
            prod = 1
            for j in range(l):
                if x_arr[j] != x_v:
                    print(f'    xwj={x_arr[j]}')
                    print(f"    curr_product={(i + 1 - x_arr[j]) / (x_v - x_arr[j])}")
                    prod = prod * (i + 1 - x_arr[j]) / (x_v - x_arr[j])

            print(f"    prod={prod}")
            value *= prod
            c_v += value

        self.cv = c_v % settings.p
        print(f"c_v={self.cv}")

        return self.cv

    def increase_threshold(self):
        pass

    def __str__(self):
        return "member-> t={}, n={}, r={}, a_coeff={}, points={}".format(self.t, self.n, self.r, self.a_coeff,
                                                                         self.points)
