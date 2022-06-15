import math

from shamir.shamir import get_shares_no_secret, get_x_values


class Dealer:
    """
        A class that implements a dealer
        calculates the polynoms and shares the points
    """

    def __init__(self, t, n):
        self.t = t
        self.n = n
        self.r = math.ceil((n - 1) / t)
        self.points_matrix = list()  # matrix of dots [[(1,1), (2,2), ...], [(1,1), (2,2), ...]] each row stands for a polynom

    def generate_polynom_list(self):
        x_list = get_x_values(self.n)
        for i in range(self.r):
            self.points_matrix.append(get_shares_no_secret(self.t, self.n, x_list))

        return self.points_matrix

    def




if __name__ == "__main__":
    d = Dealer(2, 5)
    print(d.generate_polynom_list())

