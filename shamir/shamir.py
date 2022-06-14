import random
import settings
from utils.math_helper import lagrange_interpolate
from numpy.polynomial.polynomial import polyval

"""
    How To Share a Secret
"""

"""

    get_secret(shares) - > s:
        shares - list of tuples
        [(1, 8), (4, 22) ... ]

        s - the secret
"""


def get_shares(k, n, s):
    """
    :raises: ValueError if n<k
    :param k: the number of shares that sufficient to know the secret
    :param n: the number of shares we share
    :param s: the secret
    :return: list of shares at the following format, [(1, 8), (4, 22) ... ]
    """

    if n < k:
        raise ValueError("Cannot create less shares then the mandatory amount inorder to interpolate the polynom")
    polynom_coefficients = [random.randrange(0, settings.p) for _ in range(k - 1)]
    polynom_coefficients.append(s)

    x_list = get_x_values(n)
    shares = [(x, polyval(x, polynom_coefficients[::-1]) % settings.p) for x in x_list]  # TODO not sure about the modulo

    print(shares) # TODO for debug remove later
    print(polynom_coefficients)  # TODO for debug remove later

    return shares


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


def get_secret(shares):
    """
    need to get bigger amount of sharers from the treash hold
    :param shares: gets a list of shares
    :return: the secret
    """

    # TODO need to ad alot of validity checks on the inputs and amount of shares
    s = lagrange_interpolate(0, [s[0] for s in shares], [s[1] for s in shares], settings.p)
    print("key = {}".format(s)) # TODO for debug remove later
    return s









if __name__ == '__main__':
    s = get_shares(4, 4, 8)
    get_secret(s)
    from scipy.interpolate import lagrange
    poly = lagrange([t[0] for t in s], [t[1] for t in s])
    print(poly)