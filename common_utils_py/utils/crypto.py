"""Crypto Utils class"""

import rsa
from ecies import encrypt, decrypt
from eth_keys import keys
from eth_utils import to_hex
from web3.auto import w3


def get_keys_from_file(keyfile_path, keyfile_password):
    with open(keyfile_path) as keyfile:
        encrypted_key = keyfile.read()
    private_key = w3.eth.account.decrypt(encrypted_key, keyfile_password)
    pk = keys.PrivateKey(private_key)

    private_key_hex = to_hex(private_key)  # hex string
    public_key_hex = to_hex(pk.public_key._raw_key)  # hex string

    return public_key_hex, private_key_hex


def get_ecdsa_public_key_from_file(keyfile_path, keyfile_password):
    with open(keyfile_path) as keyfile:
        encrypted_key = keyfile.read()
    private_key = w3.eth.account.decrypt(encrypted_key, keyfile_password)
    pk = keys.PrivateKey(private_key)

    return to_hex(pk.public_key._raw_key)  # hex string


def ecdsa_encription_from_file(message, provider_key_file, provider_password):
    public_key_hex = get_ecdsa_public_key_from_file(provider_key_file, provider_password)
    encrypted_message = encryption(public_key_hex, message.encode())
    hash = to_hex(encrypted_message)
    return hash, public_key_hex


def ecdsa_decryption(message, provider_key_file, provider_password):
    (public_key_hex, private_key_hex) = get_keys_from_file(provider_key_file, provider_password)
    result = decryption(private_key_hex, message)
    return result.decode()


def rsa_encription_from_file(message, rsa_public_key_file):
    pub_key = get_rsa_public_key_from_file(rsa_public_key_file)
    encrypted_message = rsa_encryption(pub_key, message.encode())
    hash = to_hex(encrypted_message)
    return hash, get_content_keyfile_from_path(rsa_public_key_file)


def rsa_decryption(message, rsa_private_key_file):
    priv_key = get_rsa_private_key_from_file(rsa_private_key_file)
    result = rsa_decryption(priv_key, message.encode())
    return result.decode()


def get_content_keyfile_from_path(keyfile_path):
    with open(keyfile_path, mode='r') as keyfile:
        key_content = keyfile.read()

    return key_content.replace('-----BEGIN PUBLIC KEY-----', '') \
        .replace('-----END PUBLIC KEY-----', '') \
        .replace('\n', '')


def get_rsa_public_key_from_file(keyfile_path):
    with open(keyfile_path, mode='rb') as keyfile:
        key_content = keyfile.read()
    return rsa.PublicKey.load_pkcs1_openssl_pem(key_content)


def get_rsa_private_key_from_file(keyfile_path):
    with open(keyfile_path, mode='rb') as keyfile:
        key_content = keyfile.read()
    return rsa.PrivateKey.load_pkcs1(key_content)


def rsa_encryption(public_key, data):
    return rsa.encrypt(data, public_key)


def rsa_decryption(private_key, encrypted_data):
    return rsa.decrypt(encrypted_data, private_key)


def encryption(public_key_hex, data):
    return encrypt(public_key_hex, data)


def decryption(private_key_hex, encrypted_data):
    return decrypt(private_key_hex, encrypted_data)

