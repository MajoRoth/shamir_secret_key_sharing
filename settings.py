import logging
p = 545579
g = 67
q = 1091159  # chosen according to the constraint: p|q-1



delta = 10**(-5)
PUBLIC_EXPONENT = 65537
KEY_SIZE = 2048

RECEIVE_BYTES = 1000000000

DEALER_HOST = "127.0.0.1"
DEALER_PORT = 5418

MEMBERS = [("127.0.0.1", 5408), ("127.0.0.1", 5402), ("127.0.0.1", 5403), ("127.0.0.1", 5404), ("127.0.0.1", 5405)]

VALIDATOR_HOST = "127.0.0.1"
VALIDATOR_PORT = 65432

SUCCESS = {
'code': 1
}

FAILURE = {
    'code': 0
}

LOG_LEVEL = logging.DEBUG


class Colors:
    server = '\033[92m'  # GREEN
    client = '\033[94m'  # BLUE
    RESET = '\033[0m'  # RESET COLOR
