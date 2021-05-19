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

    did_seed = generate_prefixed_id()
    asset_id = did_registry.hash_did(did_seed, publisher_account.address)

    asset1 = ddo_sample_2
    asset1._did = DID.did(asset_id)
    did_registry.register(did_seed, checksum_test, url=value_test, account=publisher_account)
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

    did_seed = generate_prefixed_id()
    asset_id = did_registry.hash_did(did_seed, register_account.address)

    did = DID.did(asset_id)

    value_test = metadata_instance.root_url
    did_resolver = DIDResolver(keeper().did_registry)
    did_registry.register(did_seed, b'test', url=value_test, account=register_account)
    url = did_resolver.get_resolve_url(Web3.toBytes(hexstr=asset_id))
    assert url == value_test


def test_get_resolve_multiple_urls(publisher_account):
    register_account = publisher_account
    did_registry = keeper().did_registry
    did_resolver = DIDResolver(keeper().did_registry)

    iterations = 3
    counter = 0

    while counter < iterations:
        _seed = generate_prefixed_id()
        _asset_id = did_registry.hash_did(_seed, register_account.address)
        _url = 'http://localhost:5000/' + str(counter)
        did_registry.register(_seed, b'test', url=_url, account=register_account)
        assert did_resolver.get_resolve_url(Web3.toBytes(hexstr=_asset_id)) == _url
        counter = counter + 1


def test_get_did_not_valid():
    did_resolver = DIDResolver(keeper().did_registry)
    with pytest.raises(TypeError):
        did_resolver.get_resolve_url('not valid')
