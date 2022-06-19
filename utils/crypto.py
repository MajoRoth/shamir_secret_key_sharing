from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

import settings


def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=settings.PUBLIC_EXPONENT,
        key_size=settings.KEY_SIZE)

    public_key = private_key.public_key()
    return private_key, public_key


def pub_key2str(pk):
    pem_public = pk.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem_public.decode()


def str2pub_key(pem_string):
    public_key = serialization.load_pem_public_key(
        pem_string.encode()
    )
    return public_key


def pr_key2str(prk):
    pem_private = prk.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    return pem_private.decode()


def str2pr_key(pem_string):
    private_key = serialization.load_pem_private_key(
        pem_string,
        password=None
    )
    return private_key


def encrypt_message(msg: bytes, public_key):
    encrypted = public_key.encrypt(
        msg,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted


def decrypt_message(encrypted, private_key):
    original_message = private_key.decrypt(
        encrypted,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return original_message
