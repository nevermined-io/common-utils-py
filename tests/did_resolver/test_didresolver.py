import logging
import secrets

import pytest
from contracts_lib_py import Keeper
from contracts_lib_py.exceptions import (
    DIDNotFound,
)
from web3 import Web3

from common_utils_py.did import DID, did_to_id
from common_utils_py.did_resolver.did_resolver import (
    DIDResolver,
)
from common_utils_py.utils.utilities import generate_prefixed_id

logger = logging.getLogger()


def keeper():
    return Keeper.get_instance()


def test_did_resolver_library(publisher_account, metadata_instance, ddo_sample_2):
    did_registry = keeper().did_registry
    checksum_test = Web3.keccak(text='checksum')
    value_test = metadata_instance.root_url

    did_resolver = DIDResolver(keeper().did_registry)
    asset1 = ddo_sample_2
    asset1._did = DID.did({"0": generate_prefixed_id()})
    #    DID.did({"0": "0x1098098"})
    did_registry.register(asset1.asset_id, checksum_test, url=value_test, account=publisher_account)
    metadata_instance.publish_asset_ddo(asset1)

    did_resolved = did_resolver.resolve(asset1.did)
    assert did_resolved
    assert did_resolved.did == asset1.did

    with pytest.raises(ValueError):
        did_resolver.resolve(asset1.asset_id)

    metadata_instance.retire_asset_ddo(asset1.did)


def test_did_not_found():
    did_resolver = DIDResolver(keeper().did_registry)
    did_id = secrets.token_hex(32)
    did_id_bytes = Web3.toBytes(hexstr=did_id)
    with pytest.raises(DIDNotFound):
        did_resolver.resolve(did_id_bytes)


def test_get_resolve_url(metadata_instance, publisher_account):
    register_account = publisher_account
    did_registry = keeper().did_registry
    did = DID.did({"0": generate_prefixed_id()})
    asset_id = did_to_id(did)
    value_test = metadata_instance.root_url
    did_resolver = DIDResolver(keeper().did_registry)
    did_registry.register(asset_id, b'test', url=value_test, account=register_account)
    url = did_resolver.get_resolve_url(Web3.toBytes(hexstr=asset_id))
    assert url == value_test


def test_get_resolve_multiple_urls(publisher_account):
    register_account = publisher_account
    did_registry = keeper().did_registry
    did = DID.did({"0": generate_prefixed_id()})
    did2 = DID.did({"0": generate_prefixed_id()})
    did3 = DID.did({"0": generate_prefixed_id()})
    did4 = DID.did({"0": generate_prefixed_id()})
    did5 = DID.did({"0": generate_prefixed_id()})
    did6 = DID.did({"0": generate_prefixed_id()})
    did7 = DID.did({"0": generate_prefixed_id()})
    did8 = DID.did({"0": generate_prefixed_id()})
    did9 = DID.did({"0": generate_prefixed_id()})
    did10 = DID.did({"0": generate_prefixed_id()})
    value_test = 'http://localhost:5000'
    value_test2 = 'http://localhost:5001'
    value_test3 = 'http://localhost:5002'
    value_test4 = 'http://localhost:5003'
    value_test5 = 'http://localhost:5004'
    value_test6 = 'http://localhost:5005'
    value_test7 = 'http://localhost:5006'
    value_test8 = 'http://localhost:5007'
    value_test9 = 'http://localhost:5008'
    value_test10 = 'http://localhost:5009'
    did_id = did_to_id(did)
    did_id2 = did_to_id(did2)
    did_id3 = did_to_id(did3)
    did_id4 = did_to_id(did4)
    did_id5 = did_to_id(did5)
    did_id6 = did_to_id(did6)
    did_id7 = did_to_id(did7)
    did_id8 = did_to_id(did8)
    did_id9 = did_to_id(did9)
    did_id10 = did_to_id(did10)
    did_resolver = DIDResolver(keeper().did_registry)
    did_registry.register(did_id, b'test', url=value_test, account=register_account)
    did_registry.register(did_id2, b'test', url=value_test2, account=register_account)
    did_registry.register(did_id3, b'test', url=value_test3, account=register_account)
    did_registry.register(did_id4, b'test', url=value_test4, account=register_account)
    did_registry.register(did_id5, b'test', url=value_test5, account=register_account)
    did_registry.register(did_id6, b'test', url=value_test6, account=register_account)
    did_registry.register(did_id7, b'test', url=value_test7, account=register_account)
    did_registry.register(did_id8, b'test', url=value_test8, account=register_account)
    did_registry.register(did_id9, b'test', url=value_test9, account=register_account)
    did_registry.register(did_id10, b'test', url=value_test10, account=register_account)
    url = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id))
    url2 = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id2))
    url3 = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id3))
    url4 = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id4))
    url5 = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id5))
    url6 = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id6))
    url7 = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id7))
    url8 = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id8))
    url9 = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id9))
    url10 = did_resolver.get_resolve_url(Web3.toBytes(hexstr=did_id10))
    assert url == value_test
    assert url2 == value_test2
    assert url3 == value_test3
    assert url4 == value_test4
    assert url5 == value_test5
    assert url6 == value_test6
    assert url7 == value_test7
    assert url8 == value_test8
    assert url9 == value_test9
    assert url10 == value_test10


def test_get_did_not_valid():
    did_resolver = DIDResolver(keeper().did_registry)
    with pytest.raises(TypeError):
        did_resolver.get_resolve_url('not valid')
