from utils import crypto
import utils.finite_field_helper as ffh
from cryptography.hazmat.primitives import hashes


class Validator:
    def __init__(self):
        self.private_key, self.public_key = crypto.generate_keys()
        self.t = None
        self.a_coeff = None
        self.hashed_secret = None

    def set_parameters(self, t, a_coeff, hashed_secret):
        self.t = t
        self.a_coeff = a_coeff
        self.hashed_secret = hashed_secret

    @staticmethod
    def secret_reconstructor_for_changeable_threshold(c_arr: list) -> float:
        """
        :param c_arr: cv values of each member
        :return:
        """
        print("c_arr: ", c_arr)

        # calculate the secret
        secret = ffh.sum(c_arr)
        return secret

    def validate_secret(self, secret):
        print('secret = ', secret)
        s = round(secret)
        h = hashes.Hash(hashes.SHA256())
        h.update(bytes(s))
        ans = h.finalize() == self.hashed_secret
        print("ans: ", ans)
        return ans





