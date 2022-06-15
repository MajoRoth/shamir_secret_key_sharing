import math
import settings
import random

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
        self.a_list = list()
        self.pop_count = 0  # private

    def generate_polynom_list(self):
        x_list = get_x_values(self.n)
        for i in range(self.r):
            self.points_matrix.append(get_shares_no_secret(self.t, self.n, x_list))

        return self.points_matrix

    def get_points_by_index(self, i):
        return [row[i] for row in self.points_matrix]

    def pop_point(self):
        if self.pop_count >= self.n:
            raise "All points were delivered"
        self.pop_count += 1
        return [row[self.pop_count - 1] for row in self.points_matrix]

    def generate_a_coeff_list(self):
        for i in range(self.r):
            self.a_list.append(random.randrange(1, settings.p))




    def __str__(self):
        return "dealer-> t={}, n={}, r={}, points={}, a_coeff={}".format(self.t, self.n, self.r, self.points_matrix, self.a_list)








if __name__ == "__main__":
    d = Dealer(2, 5)
    print(d.generate_polynom_list())
    print(d.get_points_by_index(0))

