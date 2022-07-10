import math
from dealer.dealer import Dealer
from member.member import Member
import settings


def main():
    # settings
    n = 6
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
    l = 5
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
        print(member.verify_my_points())
        print(str(member))
        print(f'cv = {cv}\n')

    print('--------------------------------------------\n')
    print("sum of cv's: {}".format(sum(c_arr[:l]) % settings.p))


if __name__ == "__main__":
    main()
