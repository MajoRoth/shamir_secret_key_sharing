import math
import random

from dealer.dealer import Dealer
from member.member import Member
import settings
import matplotlib.pyplot as plt
from datetime import datetime
from utils.finite_field_helper import sum

def generate_and_validate(n, t, l):
    r = math.ceil((n - 1) / t)
    # print(f"params: n = {n}, t = {t}, r = {r}")
    dealer = Dealer(t=t, n=n, RSA=False)
    dealer.generate_a_coeff_list()
    dealer.generate_polynomial_list_and_g_matrix()
    print(dealer.share_generation())
    # print('the secret is: ', dealer.share_generation())

    # create n members -> each one with his own shares. change the threshold to l
    c_arr = []
    members_list = []
    idx_list = []
    for i in range(1, n):
        idx_list.append(i)
        member = Member(RSA=False)
        member.set_parameters(t, n, dealer.a_coeff, dealer.get_x_arr(), dealer.get_g_matrix(), dealer.pop_points())
        member.current_l = l
        cv = member.calculate_cv()
        c_arr.append(cv)
        members_list.append(member)

        # print("member number: {}".format(i))
        # print(member.verify_my_points())
        # print(str(member))
        # print(f'cv = {cv}\n')

    # print('--------------------------------------------\n')
    # print("sum of cv's: {}".format(sum(c_arr[:l]) % settings.p))


def members():
    t = datetime.now()
    # generate_and_validate(7, 4, 5)
    print(datetime.now() - t)

    output_list = []
    x_list = []
    N = 400

    for i in range(1, N):
        x_list.append(i)
        t = datetime.now()
        generate_and_validate(4 + i, 1 + math.floor(i / 4), 2 + math.floor(i / 2))
        output_list.append((datetime.now() - t).total_seconds())

        print(i)

    print(x_list)
    print(output_list)

    plt.plot(x_list, output_list)
    plt.title("Running time [ms] vs number pf members")
    plt.xlabel("Number of members")
    plt.ylabel("Running time [ms]")
    plt.show()


def calc_secret():
    n = 10
    t = 8
    r = math.ceil((n - 1) / t)
    # print(f"params: n = {n}, t = {t}, r = {r}")
    dealer = Dealer(t=t, n=n, RSA=False)
    dealer.generate_a_coeff_list()
    dealer.generate_polynomial_list_and_g_matrix()
    # print('the secret is: ', dealer.share_generation())

    # create n members -> each one with his own shares. change the threshold to l
    c_arr = []
    members_list = []
    idx_list = []
    for i in range(1, n + 1):
        idx_list.append(i)
        member = Member(RSA=False)
        member.set_parameters(t, n, dealer.a_coeff, dealer.get_x_arr(), dealer.get_g_matrix(), dealer.pop_points())
        member.current_l = t
        cv = member.calculate_cv()
        c_arr.append(cv)
        members_list.append(member)


if __name__ == "__main__":
    members()

