from scipy.interpolate import lagrange
import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial.polynomial import Polynomial





if __name__ == '__main__':
    """
        https://numpy.org/doc/stable/reference/routines.polynomials.html
    """
    x = np.array([0, 1, 2, 3])
    y = x ** 3
    poly = lagrange(x, y)
    print(poly)
    print(Polynomial(poly.coef[::-1]).coef)

    x_new = np.arange(0, 3.1, 0.1)
    plt.scatter(x, y, label='data')
    plt.plot(x_new, Polynomial(poly.coef[::-1])(x_new), label='Polynomial')
    plt.plot(x_new, 3 * x_new ** 2 - 2 * x_new + 0 * x_new, label = r"$3 x^2 - 2 x$", linestyle = '-.')
    plt.legend()
    plt.show()