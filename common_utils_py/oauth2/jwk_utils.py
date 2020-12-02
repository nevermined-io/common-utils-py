"""Helper functions to convert between eth keys and JWK

This only works for EC curve secp256k1.
"""
import base64
from common_utils_py.utils.crypto import get_keys_from_file


def key_bytes_to_jwk(public_key_bytes, private_key_bytes):
    jwk_json = {
        "kty": "EC",
        "crv": "secp256k1",
        "d": base64.urlsafe_b64encode(private_key_bytes),
        "x": base64.urlsafe_b64encode(public_key_bytes[:32]),
        "y": base64.urlsafe_b64encode(public_key_bytes[32:])
    }

    return jwk_json


def key_file_to_jwk(keyfile_path, password):
    public_key_hex, private_key_hex = get_keys_from_file(keyfile_path, password)
    private_key_bytes = bytes.fromhex(private_key_hex[2:])
    public_key_bytes = bytes.fromhex(public_key_hex[2:])
    
    return key_bytes_to_jwk(public_key_bytes, private_key_bytes)


def account_to_jwk(account):
    return key_file_to_jwk(account.key_file, account.password)