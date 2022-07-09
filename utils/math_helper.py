import numpy as np


def eval_at(poly, x, prime):
    """Evaluates polynomial (coefficient tuple) at x, used to generate a
    shamir pool in make_random_shares below.
    """
    accum = 0
    for coeff in poly:
        accum *= x
        accum += coeff
        accum %= prime  # TODO the division of prime is here
    return accum


def extended_gcd(a, b):
    """
    Copied from wikipedia
    calculates the inverse of a mod p
    """
    x = 0
    last_x = 1
    y = 1
    last_y = 0
    while b != 0:
        quot = a // b
        a, b = b, a % b
        x, last_x = last_x - quot * x, x
        y, last_y = last_y - quot * y, y
    return last_x, last_y


def divmod(a, b, p):
    """
    Copied from wikipedia
    calculates a / b mod p
    """
    inv, _ = extended_gcd(b, p)
    return (a * inv) % p


def lagrange_interpolate(x, x_s, y_s, p):
    """
    Find the y-value for the given x, given n (x, y) points;
    k points will define a polynomial of up to kth order.
    """
    k = len(x_s)

    nums = []  # avoid inexact division
    dens = []
    for i in range(k):
        others = list(x_s)
        cur = others.pop(i)
        nums.append(np.prod(list(x - o for o in others)))
        dens.append(np.prod(list(cur - o for o in others)))
    den = np.prod(list(dens))
    from utils.new_math_helper import div, mul
    num = sum([div(mul(mul(nums[i], den), y_s[i]), dens[i]) for i in range(k)])
    return (divmod(num, den, p) + p) % p
