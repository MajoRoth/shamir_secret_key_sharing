import math
from utils import crypto
from utils import finite_field_helper as ffh
import settings


class Member:
    def __init__(self, RSA=True):
        if RSA:
            self.private_key, self.public_key = crypto.generate_keys()
        self.t = None
        self.n = None
        self.r = None
        self.a_coeff = None
        self.points = None
        self.g_coff = None
        self.current_l = None
        self.cv = None
        self.x_arr = None
        self.g_matrix = None

    def set_parameters(self, t: int, n: int, a_coeff, x_arr, g_matrix, points: list = None):
        self.t = t
        self.n = n
        self.r = math.ceil((n - 1) / t)
        self.a_coeff = a_coeff
        self.points = points
        self.current_l = t
        self.x_arr = x_arr
        self.cv = None
        self.g_matrix = g_matrix

    def get_my_x(self):
        return self.points[0][0]

    def get_my_y_list(self):
        return [p[1] for p in self.points]

    def verify_my_points(self):
        # given my g_matrix check if the
        g_matrix = self.g_matrix  # mod q
        x = self.get_my_x()
        x_pow = []
        t = self.t

        for i in range(t):
            x_pow.append(x ** i)  # i<t
        x_pow.reverse()

        for i, (x, y) in enumerate(self.points):
            g_y = pow(settings.g, y, settings.q)
            g_coff = g_matrix[i]
            verify = 1

            for j in range(t):
                verify = verify * pow(g_coff[j], x_pow[j], settings.q) % settings.q

            if verify != g_y:
                return False

        return True

    def calculate_cv(self) -> float:
        """
        :param x_arr: arr of the members x-es
        :param l: the current threshold
        :return: the c value of this member
        """
        x_arr = self.x_arr
        l = self.current_l
        c_v = 0
        y_arr = self.get_my_y_list()
        x_v = self.get_my_x()

        for i in range(self.r):
            value = ffh.add(self.a_coeff[i], y_arr[i])

            # calculate the product value
            prod = 1
            for j in range(l):
                if x_arr[j] != x_v:
                    prod = ffh.mul(prod, ffh.div((i + 1 - x_arr[j]), (x_v - x_arr[j])))

            value = ffh.mul(value, prod)
            c_v = ffh.add(c_v, value)

        self.cv = c_v % settings.p
        print(f"c_v={self.cv}")

        return self.cv

    def is_empty(self):
        if self.t is None and self.n is None and self.r is None and self.a_coeff is None and self.points is None \
                and self.current_l is None and self.cv is None:
            return True
        return False

    def __str__(self):
        return "member-> t={}, n={}, r={}, a_coeff={}, points={}".format(self.t, self.n, self.r, self.a_coeff,
                                                                         self.points)
