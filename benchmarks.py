import math
from dealer.dealer import Dealer
from member.member import Member
import settings
import matplotlib.pyplot as plt
from datetime import datetime

def generate_and_validate(n, t, l):
    r = math.ceil((n - 1) / t)
    print(f"params: n = {n}, t = {t}, r = {r}")
    dealer = Dealer(t=t, n=n, RSA=False)
    dealer.generate_a_coeff_list()
    dealer.generate_polynomial_list_and_g_matrix()
    print('the secret is: ', dealer.share_generation())

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

        print("member number: {}".format(i))
        print(member.verify_my_points())
        print(str(member))
        print(f'cv = {cv}\n')

    print('--------------------------------------------\n')
    print("sum of cv's: {}".format(sum(c_arr[:l]) % settings.p))



def main():
    t = datetime.now()
    generate_and_validate(7, 4, 5)
    print(datetime.now()-t)

    output_list = []
    x_list = []
    N = 10

    for i in range(1, N):
        x_list.append(i)
        t = datetime.now()
        generate_and_validate(5+i, 4 + i, 4 + i)
        output_list.append((datetime.now() - t).total_seconds())

        print(i)

    print(x_list)
    print(output_list)

    plt.plot(x_list, output_list)
    plt.title("Avg max score vs number of calls to random CSP")
    plt.xlabel("num of calls")
    plt.ylabel("avg max score")
    plt.show()
    # plt.save("avg max score")


if __name__ == "__main__":
    main()
