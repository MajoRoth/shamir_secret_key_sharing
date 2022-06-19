import logging
p = 10**2 + 9
delta = 10**(-5)


RECEIVE_BYTES = 4096

DEALER_HOST = "127.0.0.1"
DEALER_PORT = 5400

MEMBER_HOST = "127.0.0.1"
MEMBER_PORT = 5401

VALIDATOR_HOST = "127.0.0.1"
VALIDATOR_PORT = 5402

SUCCESS = {
    'code': 1
}

FAILURE = {
    'code': 0
}

LOG_LEVEL = logging.DEBUG
