from utils.shamir import get_shares, get_secret
import settings
from utils.math_helper import eval_at


def calculate_cv(points_list, x_arr, l, r, n, a_coeff) -> float:
    """
    :param x_arr: arr of the members x-es
    :param l: the current threshold
    :return: the c value of this member
    """
    c_v = 0
    y_arr = [x[1] for x in points_list]
    x_v = points_list[0][0]
    # print(f"\nx_arr={x_arr}")

    for i in range(r):
        # print(f"ai={self.a_coeff[i]}, hi[xwv]={y_arr[i]}, xwv={x_v}, i={i + 1}")
        value = a_coeff[i] * y_arr[i]

        # calculate the product value
        prod = 1
        for j in range(l):
            if x_arr[j] != x_v:
                # print(f'    xwj={x_arr[j]}')
                # print(f"    curr_product={(i + 1 - x_arr[j]) / (x_v - x_arr[j])}")
                prod = prod * ((i +1 - x_arr[j]) / (x_v - x_arr[j])) % settings.p

        # print(f"    prod={prod}")
        value *= prod
        c_v += value

    cv = c_v % settings.p
    return cv

def gen_secret(r, a_list, poly_mat):
    val = 0
    for i in range(r):
        val += a_list[i] * eval_at(poly_mat[i], i+1, settings.p)

    return val % settings.p


def main():
    n = 5
    t = 2
    r = 2
    x_list = [3,4,5,6,7]
    shares_arr = []
    polys_arr = []
    poly = [
        [1, 1],
        [2, 1]
    ]
    a_coeff = [1,2]
    print(gen_secret(r, a_coeff, poly))
    for i in range(r):
        shares, original_poly_coeff = get_shares(n=n, k=t, s=1, x_list=x_list, polynom_coefficients=poly[i])
        shares_arr.append(shares)
        polys_arr.append(original_poly_coeff)
        print("poly number: {}".format(i))
        print(shares)
        print(original_poly_coeff)
        print(get_secret(shares))

    members_mat = list()
    sum = 0
    l=4  # here inbal
    for i in range(l):
        member_arr = []
        for j in range(r):
            member_arr.append(shares_arr[j][i])

        print("member number: {}".format(i))
        print(member_arr)
        members_mat.append(member_arr)
        cv = calculate_cv(points_list=member_arr, x_arr=x_list, l=l, r=r, n=n, a_coeff=a_coeff)
        sum += cv
        print(cv)

    print("sum of cv's: {}".format(sum % settings.p))


    from scipy.interpolate import lagrange
    import matplotlib.pyplot as plt
    import numpy as np
    from numpy.polynomial.polynomial import Polynomial




    #print("original poly y_0 {}, lagrange y_0 {}".format(Polynomial(original_poly(0), poly(0))))
    #
    # x_new = np.arange(-1, 10, 1)
    #
    # fig, ax = plt.subplots()
    # ax.grid(True, which='both')
    #
    # ax.scatter(x, y, label='data')
    #
    # y_new = [lagrange_interpolate(t, x, y, settings.p) for t in x_new]
    #
    # ax.plot(x_new, Polynomial(poly.coef[::-1])(x_new), label='lagrange polynom')
    # ax.plot(x_new, y_new, label='lagrange polynom modulo')
    # # plt.plot(x_new, 3 * x_new ** 2 - 2 * x_new + 0 * x_new, label = r"$3 x^2 - 2 x$", linestyle = '-.')
    # plt.legend()
    #
    # plt.show()




if __name__ == "__main__":
    main()