import math
import random

from dealer.dealer import Dealer
from member.member import Member

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

    for i in range(r):
        value = a_coeff[i] * y_arr[i]

        # calculate the product value
        prod = 1
        for j in range(l):
            if x_arr[j] != x_v:
                prod = prod * ((i + 1 - x_arr[j]) / (x_v - x_arr[j])) % settings.p

        value *= prod
        c_v += value

    cv = c_v % settings.p
    return cv


def gen_secret(r, a_list, poly_mat):
    val = 0
    for i in range(r):
        val += a_list[i] * eval_at(poly_mat[i], i + 1, settings.p)

    return val % settings.p


def main():
    # settings
    n = 10
    t = 4
    r = math.ceil((n - 1) / t)
    print(f"params: n = {n}, t = {t}, r = {r}")
    print('--------------------------------------------\n')

    # generate secret & polynomials & shares
    dealer = Dealer(t=t, n=n)
    dealer.generate_a_coeff_list()
    dealer.generate_polynomial_list_and_g_matrix()
    print('the secret is: ', dealer.share_generation())  # calculate the secret with A1 algorithm

    print('\n--------------------------------------------\n')

    # create n members -> each one with his own shares. change the threshold to l
    l = 4
    c_arr = []
    members_list = []
    idx_list = []
    for i in range(n):
        idx_list.append(i+1)
        member = Member()
        member.set_parameters(t, n, dealer.a_coeff, dealer.get_x_arr(), dealer.get_g_matrix(), dealer.pop_points())
        member.current_l = l
        cv = member.calculate_cv()
        c_arr.append(cv)
        members_list.append(member)

        print("member number: {}".format(i))
        print(str(member))
        print(f'cv = {cv}\n')

    print('--------------------------------------------\n')
    print("sum of cv's: {}".format(sum(c_arr[:l]) % settings.p))

    # # for each member
    # members_mat = list()
    # sum = 0
    # l = 3
    # for i in range(l):
    #     member_arr = []
    #     for j in range(r):
    #         member_arr.append(shares_arr[j][i])
    #
    #     print("member number: {}".format(i))
    #     print(f'member_arr: {member_arr}')
    #     members_mat.append(member_arr)
    #     cv = calculate_cv(points_list=member_arr, x_arr=x_list, l=l, r=r, n=n, a_coeff=a_coeff)
    #     sum += cv
    #     print(f'cv: {cv}\n')
    #
    # print("sum of cv's: {}".format(sum % settings.p))


if __name__ == "__main__":
    main()
