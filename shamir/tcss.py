import math
import numpy as np

from utils.math_helper import lagrange_interpolate
import settings


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


def share_generation(t: int, shareholders: list, p: int, a_coeff: np.array, n: int) -> int:
    r = math.ceil((n - 1) / t)  # polynomials num

    # get the polynomials
    polynomials = get_polynomials(r, shareholders)

    # create h(i) vector
    h_i = np.array([poly(i + 1) for i, poly in enumerate(polynomials)])

    # get the secret
    secret = a_coeff.dot(h_i) % p

    return secret