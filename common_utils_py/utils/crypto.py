"""Crypto Utils class"""
import base64

import rsa
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from ecies import decrypt, encrypt
from eth_keys import keys
from eth_utils import to_bytes, to_hex
from web3.auto import w3

BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]


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


def ecdsa_encryption_from_file(message, provider_key_file, provider_password):
    public_key_hex = get_ecdsa_public_key_from_file(provider_key_file, provider_password)
    encrypted_message = encryption(public_key_hex, message.encode())
    hash = to_hex(encrypted_message)
    return hash, public_key_hex


def ecdsa_decryption(message, provider_key_file, provider_password):
    (public_key_hex, private_key_hex) = get_keys_from_file(provider_key_file, provider_password)
    result = decryption(private_key_hex, to_bytes(hexstr=message))
    return result.decode()


def rsa_encryption_from_file(message, rsa_public_key_file):
    pub_key = get_rsa_public_key_from_file(rsa_public_key_file)
    encrypted_message, aes_encrypted_key = rsa_encryption(pub_key, message.encode())
    hash = to_hex(encrypted_message) + '|' + to_hex(aes_encrypted_key)
    return hash, get_content_keyfile_from_path(rsa_public_key_file)


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
    aes_key = rsa.randnum.read_random_bits(128)
    encrypted_data = aes_encryption(data, aes_key)
    encrypted_aes_key = rsa.encrypt(aes_key, public_key)
    return encrypted_data, encrypted_aes_key


def rsa_decryption_aes(message, rsa_private_key_file):
    if '|' in message:  # The message includes an encrypted AES key
        tokens = message.split('|')
        return rsa_decryption(get_rsa_private_key_from_file(rsa_private_key_file),
                              to_bytes(hexstr=tokens[0]), to_bytes(hexstr=tokens[1]))
    priv_key = get_rsa_private_key_from_file(rsa_private_key_file)
    result = rsa.decrypt(to_bytes(hexstr=message), priv_key)
    return result.decode()


def rsa_decryption(private_key, encrypted_data, encrypted_aes_key):
    aes_key = rsa.decrypt(encrypted_aes_key, private_key)
    return aes_decryption(encrypted_data, aes_key)


def get_aes_private_key(passphrase):
    salt = b'this is a salt'
    kdf = PBKDF2(passphrase, salt, 64, 1000)
    key = kdf[:32]
    return key


def aes_encryption(data, passphrase):
    data = data.decode()
    private_key = get_aes_private_key(passphrase)
    data = pad(data).encode()
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(data))


def aes_decryption(encrypted_data, passphrase):
    private_key = get_aes_private_key(passphrase)
    encrypted_data = base64.b64decode(encrypted_data)
    iv = encrypted_data[:16]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(encrypted_data[16:]))


def encryption(public_key_hex, data):
    return encrypt(public_key_hex, data)


def decryption(private_key_hex, encrypted_data):
    return decrypt(private_key_hex, encrypted_data)
