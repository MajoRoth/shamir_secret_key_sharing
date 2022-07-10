import random
import settings
from utils.finite_field_helper import lagrange_interpolate, eval_at

"""
    How To Share a Secret
"""


def get_shares(k, n, s, x_list=None, polynom_coefficients = None):
    """
    :param polynom_coefficients:
    :param x_list:
    :raises: ValueError if n<k
    :param k: the number of shares that sufficient to know the secret
    :param n: the number of shares we share
    :param s: the secret
    :return: list of shares at the following format, [(1, 8), (4, 22) ... ]
    """

    if n < k:
        raise ValueError("Cannot create less shares then the mandatory amount inorder to interpolate the polynom")

    if polynom_coefficients is None:
        polynom_coefficients = [random.randrange(0, settings.p) for _ in range(k - 1)]
        polynom_coefficients.append(s)

    if x_list is None:
        x_list = get_x_values(n)

    shares = [(x, eval_at(polynom_coefficients, x)) for x in x_list]

    # print("polynomial coefficients: ", polynom_coefficients)  # TODO for debug remove later
    # print("shares points:", shares)  # TODO for debug remove later

    return shares, polynom_coefficients  # TODO return polynom_coefficients for debug, rmove it later


def get_shares_and_g_matrix(k, n, s, x_list=None):
    """
    :raises: ValueError if n<k
    :param k: the number of shares that sufficient to know the secret
    :param n: the number of shares we share
    :param s: the secret
    :return: list of shares at the following format, [(1, 8), (4, 22) ... ], [g**a0, g**a1,.., g**a(k-1)]
    """

    if n < k:
        raise ValueError("Cannot create less shares then the mandatory amount inorder to interpolate the polynom")
    polynom_coefficients = [random.randrange(0, settings.p) for _ in range(k - 1)]
    polynom_coefficients.append(s)
    print("poly coeff {}".format( polynom_coefficients))
    random.seed(0)

    g_polynom_coefficients = list()

    for i in range(len(polynom_coefficients)):
        g_polynom_coefficients.append(
            pow(settings.g, polynom_coefficients[i], settings.q)
        )

    print(g_polynom_coefficients)

    if x_list == None:
        x_list = get_x_values(n)

    shares = [(x, eval_at(polynom_coefficients, x)) for x in x_list]

    # print("shares points:", shares)  # TODO for debug remove later
    # print("polynomial coefficients: ", polynom_coefficients)  # TODO for debug remove later
    # print("g polynomial coefficients: ", g_polynom_coefficients)  # TODO for debug remove later
    return shares, g_polynom_coefficients  # TODO return polynom_coefficients for debug, rmove it later


def get_shares_no_secret(k, n, x_list=None):
    """
        :raises: ValueError if n<k
        :param k: the number of shares that sufficient to know the secret
        :param n: the number of shares we share
        :return: list of shares at the following format, [(1, 8), (4, 22) ... ] with a random secret
    """
    return get_shares(k, n, random.randrange(0, settings.p), x_list=x_list)


def get_shares_no_secret_and_g_matrix(k, n, x_list=None):
    """
        :raises: ValueError if n<k
        :param k: the number of shares that sufficient to know the secret
        :param n: the number of shares we share
        :return: list of shares at the following format, [(1, 8), (4, 22) ... ] with a random secret, g_coff for the specific polynom
    """
    return get_shares_and_g_matrix(k, n, random.randrange(0, settings.p), x_list=x_list)


def get_secret(shares, idx=0):
    """
    find the y value of a function according to the points in a specific index
    need to get bigger amount of shares from the threshold
    :param shares: gets a list of points
    :param idx:
    :return: the secret
    """

    # TODO need to ada a lot of validity checks on the inputs and amount of shares
    secret = lagrange_interpolate(idx, [s[0] for s in shares], [s[1] for s in shares])
    return secret


def get_x_values(n, p=settings.p):
    """
    :param n: the number of values to generate
    :param p: the max value of the field
    :return: list of unique and random x values in (0, p)
    """
    x_list = list()
    while len(x_list) != n:
        x = random.randrange(1, p)
        if x not in x_list:
            x_list.append(x)

    return x_list


if __name__ == '__main__':
    s, original_poly_coeff = get_shares(4, 4, 8)
    get_secret(s)

    from scipy.interpolate import lagrange
    import matplotlib.pyplot as plt
    import numpy as np
    from numpy.polynomial.polynomial import Polynomial

    x = [t[0] for t in s]
    y = [t[1] for t in s]

    poly = lagrange(x, y)
    print(poly)
    # print("original poly y_0 {}, lagrange y_0 {}".format(Polynomial(original_poly(0), poly(0))))

    x_new = np.arange(-1, 10, 1)

    fig, ax = plt.subplots()
    ax.grid(True, which='both')

    ax.scatter(x, y, label='data')

    y_new = [lagrange_interpolate(t, x, y) for t in x_new]

    ax.plot(x_new, Polynomial(poly.coef[::-1])(x_new), label='lagrange polynom')
    ax.plot(x_new, y_new, label='lagrange polynom modulo')
    # plt.plot(x_new, 3 * x_new ** 2 - 2 * x_new + 0 * x_new, label = r"$3 x^2 - 2 x$", linestyle = '-.')
    plt.legend()

    plt.show()
