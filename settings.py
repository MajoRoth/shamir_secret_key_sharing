import logging
p = 10**4 + 9
g=
q=
# Pick q, p primes such that q | p - 1

delta = 10**(-5)
PUBLIC_EXPONENT = 65537
KEY_SIZE = 2048

RECEIVE_BYTES = 4096

DEALER_HOST = "127.0.0.1"
DEALER_PORT = 5411

MEMBERS = [("127.0.0.1", 5408), ("127.0.0.1", 5402), ("127.0.0.1", 5403), ("127.0.0.1", 5404), ("127.0.0.1", 5405)]

VALIDATOR_HOST = "127.0.0.1"
VALIDATOR_PORT = 5407

SUCCESS = {
    'code': 1
}

FAILURE = {
    'code': 0
}

LOG_LEVEL = logging.DEBUG
