# https://jeremykun.com/2014/03/13/programming-with-finite-fields/
import settings

P = settings.p


def extendedEuclideanAlgorithm(a, b):
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
    print(type(a), type(b))
    a = a % P
    b = b % P
    return (a * b) % P


def add(a, b):
    a = a % P
    b = b % P
    return (a + b) % P
