from scipy.interpolate import lagrange
import numpy as np
from numpy.polynomial.polynomial import Polynomial
import math


class Shareholder:
    def __init__(self, x_share: int, ys_share: np.array):
        self.points = [(x_share, y_share) for y_share in ys_share]


def get_polynomials(r: int, shareholders: list) -> list:
    """
    create for each polynomial list of it's x-s and y-s, and calculate the polynomial using lagrange.
    :param r: amount of polynomials
    :param shareholders: list of Shareholder
    :return: list of the polynomials
    """

    polynomials = []
    for i in range(r):
        x = [s.points[i][0] for s in shareholders]
        y = [s.points[i][1] for s in shareholders]
        curr_poly = lagrange(x, y)
        polynomials.append(Polynomial(curr_poly.coef[::-1]))
    return polynomials


# A1 from the article:
def share_generation(t: int, shareholders: list, p: int, a_coeff: np.array, n: int) -> int:
    r = math.ceil((n - 1) / t)  # polynomials num

    # get the polynomials
    polynomials = get_polynomials(r, shareholders)

    # create h(i) vector
    h_i = np.array([poly(i + 1) for i, poly in enumerate(polynomials)])

    # get the secret
    secret = a_coeff.dot(h_i) % p

    return secret


def main_for_A1():
    n = 5  # num of shareholders
    t = 2  # t = num of functions
    p = 100

    pols = [Polynomial([1, 1]), Polynomial([1, 2])]
    a_coeff = np.array([1, 2])  # len(a) = t

    shareholders = [Shareholder(3, [pols[0](3), pols[1](3)]), Shareholder(4, [pols[0](4), pols[1](4)]),
                    Shareholder(5, [pols[0](5), pols[1](5)]), Shareholder(6, [pols[0](6), pols[1](6)]),
                    Shareholder(7, [pols[0](7), pols[1](7)])]

    s = share_generation(t, shareholders, p, a_coeff, n)
    print(s)


# A2 from the article:
def calculate_cv(v: int, a_coeff: np.array, polynomials: list, x_arr:list, p: int, l: int):
    r = len(polynomials)

    c_v = 0
    x_v = x_arr[v]
    for i in range(r):
        value = a_coeff[i] * polynomials[i](x_v) % p

        # calculate the product value
        prod = 1
        for j in range(l):
            if j != v:
                prod *= (i+1-x_arr[j])/(x_v - x_arr[j]) % p

        value *= prod % p

        c_v += value % p

    return c_v


def secret_reconstructor_for_changeable_threshold(l: int, shareholders: list, p: int, a_coeff: np.array, r: int) -> float:
    """
    just for me:
    ** we can only increase the threshold
    Each shareholder has r shares corresponding to r different polynomials with t − 1 degree each.
    Since each shareholder reveals a linear combination of these r shares in the secret reconstruction for a different
    threshold value l, we will show that the secret can only be recovered if there are l or more than l shareholders
    participated in the process.

    :param l: threshold value
    :param shareholders: list of Shareholder
    :param p: prime constant
    :param a_coeff: public coefficient list
    :return: the secret key
    """
    # get the polynomials
    polynomials = get_polynomials(r, shareholders)

    x_arr = [s.points[0][0] for s in shareholders]

    # calculate c value for each shareholder
    c_arr = [calculate_cv(v, a_coeff, polynomials, x_arr, p, l) for v in range(l)]
    # calculate c value for each shareholder
    # c_arr = [m.calculate_cv(v, x_arr, l) % settings.p for v, m in enumerate(members)]

    # calculate the secret
    secret = sum(c_arr) % p

    return secret


def main_for_A2():
    t = 2  # t = num of functions
    l = 3  # threshold
    p = 100

    pols = [Polynomial([1, 1]), Polynomial([1, 2])]
    a_coeff = np.array([1, 2])  # len(a) = t

    shareholders = [Shareholder(3, [pols[0](3), pols[1](3)]), Shareholder(4, [pols[0](4), pols[1](4)]),
                    Shareholder(5, [pols[0](5), pols[1](5)])]

    # TODO understand how the clients know r
    s = secret_reconstructor_for_changeable_threshold(l, shareholders, p, a_coeff, r=len(pols))
    print(s)


if __name__ == '__main__':
    main_for_A2()
