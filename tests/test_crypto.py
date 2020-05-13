from ecies import encrypt, decrypt
from ecies.utils import generate_eth_key

from common_utils_py.utils.crypto import decryption, encryption, get_keys_from_file, get_rsa_public_key_from_file, \
    get_rsa_private_key_from_file, rsa_encryption, rsa_decryption, aes_encryption, aes_decryption

PROVIDER_KEY_FILE = 'tests/resources/data/publisher_key_file.json'
PROVIDER_PASSWORD = 'node0'
PROVIDER_ADDRESS = '0x00bd138abd70e2f00903268f3db08f2d25677c9e'
RSA_PRIVKEY_FILE = 'tests/resources/data/rsa_priv_key.pem'
RSA_PUBKEY_FILE = 'tests/resources/data/rsa_pub_key.pem'


def test_encryption_decryption():
    eth_k = generate_eth_key()
    private_key_hex = eth_k.to_hex()  # hex string
    public_key_hex = eth_k.public_key.to_hex()  # hex string
    data = 'hi there'
    result = decrypt(private_key_hex, encrypt(public_key_hex, data.encode()))
    print(result)
    print('decoded=' + result.decode())
    assert result == data.encode()
    assert data == result.decode()


def test_encryption_decryption_with_credentials():
    keyfile_path = PROVIDER_KEY_FILE
    keyfile_password = PROVIDER_PASSWORD

    print('KeyFile Path = ' + keyfile_path)

    (public_key_hex, private_key_hex) = get_keys_from_file(keyfile_path, keyfile_password)

    data = b'hi there'
    assert data == decryption(private_key_hex, encryption(public_key_hex, data))
    assert b'it should fail' != decryption(private_key_hex, encryption(public_key_hex, b'kdas'))


def test_rsa_encryption_decryption():
    pub_key = get_rsa_public_key_from_file(RSA_PUBKEY_FILE)
    priv_key = get_rsa_private_key_from_file(RSA_PRIVKEY_FILE)

    data = b'hi there'
    encrypted_data, encrypted_aes_key = rsa_encryption(pub_key, data)
    assert data == rsa_decryption(priv_key, encrypted_data, encrypted_aes_key)

    encrypted_data, encrypted_aes_key = rsa_encryption(pub_key, b'kdas')
    assert b'it should fail' != rsa_decryption(priv_key, encrypted_data, encrypted_aes_key)


def test_rsa_encryption_decryption_long():
    pub_key = get_rsa_public_key_from_file(RSA_PUBKEY_FILE)
    priv_key = get_rsa_private_key_from_file(RSA_PRIVKEY_FILE)

    data = b'hi there, this is a much longer message that should failing during the encryption if you' \
           b'dont use an alternative approach. So this test tries to check the new flow works with ' \
           b'longer messages'
    encrypted_data, encrypted_aes_key = rsa_encryption(pub_key, data)
    assert data == rsa_decryption(priv_key, encrypted_data, encrypted_aes_key)


def test_aes_encryption_decryption():
    passphrase = 'my passphrase'

    data = b'hi there, this is a much longer message that should failing during the encryption if you' \
           b'dont use an alternative approach. So this test tries to check the new flow works with ' \
           b'longer messages'
    encrypted_data = aes_encryption(data, passphrase)
    assert data == aes_decryption(encrypted_data, passphrase)


