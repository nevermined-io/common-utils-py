"""Utilities class"""

import hashlib
import json
import uuid
from datetime import datetime

import web3
from web3 import Web3


def generate_new_id():
    """
    Generate a new id without prefix.

    :return: Id, str
    """
    return uuid.uuid4().hex + uuid.uuid4().hex


def generate_prefixed_id():
    """
    Generate a new id prefixed with 0x that is used as identifier for the service agreements ids.

    :return: Id, str
    """
    return f'0x{generate_new_id()}'


def to_32byte_hex(web3, val):
    """

    :param web3:
    :param val:
    :return:
    """
    return web3.toBytes(val).rjust(32, b'\0')


def convert_to_bytes(web3, data):
    """

    :param web3:
    :param data:
    :return:
    """
    return web3.toBytes(text=data)


def convert_to_string(web3, data):
    """

    :param web3:
    :param data:
    :return:
    """
    return web3.toHex(data)


def convert_to_text(web3, data):
    """

    :param web3:
    :param data:
    :return:
    """
    return web3.toText(data)


def checksum(seed):
    """Calculate the hash3_256."""
    return hashlib.sha3_256(
        (json.dumps(dict(sorted(seed.items(), reverse=False))).replace(" ", "")).encode(
            'utf-8')).hexdigest()


def get_timestamp():
    """Return the current system timestamp."""
    return f'{datetime.utcnow().replace(microsecond=0).isoformat()}Z'


def to_checksum_addresses(addresses):
    """
    Calculate the checksum of an addresses array

    :param addresses: Address, hex str[]
    :return: address, hex str[]
    """

    hash = []
    for address in addresses:
        hash.append(Web3.toChecksumAddress(address))
    return hash
