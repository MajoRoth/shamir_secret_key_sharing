import random
from settings import p
from numpy.polynomial.polynomial import polyval

"""
    How To Share a Secret
"""

"""
    API
    get_shares(k, n, s) -> shares:
        k - the number of shares that sufficent to know the secret
        n - the number of shares we share
        s - the secret

        shares - list of tuples
        [(1, 8), (4, 22) ... ]


    combine get_secret(shares) - > s:
        shares - list of tuples
        [(1, 8), (4, 22) ... ]

        s - the secret
"""


def get_shares(k, n, s):
    if n < k:
        raise ValueError("Cannot create less shares then the mandatory amount inorder to interpolate the polynom")
    polynom_coefficients = [random.randrange(0, p) for _ in range(k - 1)]
    polynom_coefficients.append(s)

    print(polynom_coefficients)
    shares = list()

    for i in range(n):
        x = random.randrange(1, p)  # TODO need yo check that the x's are unique
        shares.append((x, polyval(x, polynom_coefficients)))

    print(shares)
    return shares

if __name__ == '__main__':
    get_shares(3, 6, 8)