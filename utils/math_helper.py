
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

def PI(vals):
    """
    :param vals: list of numbers
    :return: the multiplicity of all of the numbers
    """
    accum = 1
    for v in vals:
        accum *= v
    return accum


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
        nums.append(PI(x - o for o in others))
        dens.append(PI(cur - o for o in others))
    den = PI(dens)
    num = sum([divmod(nums[i] * den * y_s[i] % p, dens[i], p)
               for i in range(k)])
    return (divmod(num, den, p) + p) % p

