import logging
# p = 11
p = 100


RECEIVE_BYTES = 4096

DEALER_HOST = "127.0.0.1"
DEALER_PORT = 5400

MEMBER_HOST = "127.0.0.1"
MEMBER_PORT = 5401

SUCCESS = {
    'code': 1
}

FAILURE = {
    'code': 0
}

LOG_LEVEL = logging.DEBUG
