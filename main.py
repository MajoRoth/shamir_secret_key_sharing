import scipy
import numpy as np
import matplotlib.pyplot as plt


# Credits to stack overflow for this code

def _poly_newton_coefficient(x, y):
    """
    x: list or np array contanining x data points
    y: list or np array contanining y data points
    """

    m = len(x)

    x = np.copy(x)
    a = np.copy(y)
    for k in range(1, m):
        a[k:m] = (a[k:m] - a[k - 1])/(x[k:m] - x[k - 1])

    return a

def newton_polynomial(x_data, y_data, x):
    """
    x_data: data points at x
    y_data: data points at y
    x: evaluation point(s)
    """
    a = _poly_newton_coefficient(x_data, y_data)
    n = len(x_data) - 1  # Degree of polynomial
    p = a[n]

    for k in range(1, n + 1):
        p = a[n - k] + (x - x_data[n - k])*p

    return p



if __name__ == '__main__':
    newton_interpolation = newton_polynomial([2., 4., 6.], [4., 16., 36.], np.array([0., 1., 2., 3., 4., 5., 6., 7.]))
    print(newton_interpolation)

    # Plotting the Newton Polynomial against the original data
    plt.figure(figsize=(12, 10))
    plt.scatter([2., 4., 6.], [4., 16., 36.])
    plt.plot([0., 1., 2., 3., 4., 5., 6., 7.], newton_interpolation, 'red')
    plt.title('Newton Polynomial Interpolation solves the simple example')
    plt.show()

