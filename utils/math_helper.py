import numpy as np
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

import settings


def eval_at(poly, x, prime):
    """Evaluates polynomial (coefficient tuple) at x, used to generate a
    shamir pool in make_random_shares below.
    """
    accum = 0
    for coeff in poly:
        accum *= x
        accum += coeff
        # accum %= prime
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
    return a * inv


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
    num = sum([divmod(nums[i] * den * y_s[i] % p, dens[i], p)
               for i in range(k)])
    return (divmod(num, den, p) + p) % p


def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=settings.PUBLIC_EXPONENT,
        key_size=settings.KEY_SIZE)

    public_key = private_key.public_key()
    return private_key, public_key


def pub_key2str(pk):
    pem_public = pk.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem_public.decode()


def str2pub_key(pem_string):
    public_key = serialization.load_pem_public_key(
        pem_string.encode()
    )
    return public_key


def pr_key2str(prk):
    pem_private = prk.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    return pem_private.decode()


def str2pr_key(pem_string):
    private_key = serialization.load_pem_private_key(
        pem_string,
        password=None
    )
    return private_key