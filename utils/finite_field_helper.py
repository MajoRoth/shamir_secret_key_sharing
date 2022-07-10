import settings

P = settings.p


def extendedEuclideanAlgorithm(a, b):
    """
    code from https://jeremykun.com/2014/03/13/programming-with-finite-fields/.
    implementation of Extended Euclidean Algorithm
    """
    if abs(b) > abs(a):
        (x, y, d) = extendedEuclideanAlgorithm(b, a)
        return y, x, d

    if abs(b) == 0:
        return 1, 0, a

    x1, x2, y1, y2 = 0, 1, 1, 0
    while abs(b) > 0:
        q, r = divmod(a, b)
        x = x2 - q * x1
        y = y2 - q * y1
        a, b, x2, x1, y2, y1 = b, r, x1, x, y1, y

    return x2, y2, a


def inverse(n):
    x, y, d = extendedEuclideanAlgorithm(n, P)
    return x % P


def div(a, b):
    a = a % P
    b = b % P
    return (a * inverse(b)) % P


def mul(a, b):
    a = a % P
    b = b % P
    return (a * b) % P


def add(a, b):
    a = a % P
    b = b % P
    return (a + b) % P


def dot(a_arr: list, b_arr: list):
    res = 0
    for a, b in zip(a_arr, b_arr):
        res = add(res, add(a, b))
    return res % P


def prod(vals: list):
    res = 1
    for v in vals:
        res = mul(res, v)
    return res


def sum(vals: list):
    res = 0
    for v in vals:
        res = add(res, v)
    return res


def eval_at(poly, x):
    """Evaluates polynomial (coefficient tuple) at x, used to generate a
    shamir pool in make_random_shares below.
    """
    res = 0
    for coeff in poly:
        res *= x
        res += coeff
    return res


def lagrange_interpolate(x, x_s: list, y_s: list):
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
        nums.append(prod(list(x - o for o in others)))
        dens.append(prod(list(cur - o for o in others)))
    den = prod(list(dens))
    num = sum([div(mul(mul(nums[i], den), y_s[i]), dens[i]) for i in range(k)])
    return add(div(num, den), P)
