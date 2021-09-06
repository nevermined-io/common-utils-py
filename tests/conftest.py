import os

import pytest
from contracts_lib_py.contract_handler import ContractHandler
from contracts_lib_py.keeper import Keeper
from contracts_lib_py.utils import get_account
from contracts_lib_py.web3_provider import Web3Provider
from web3 import HTTPProvider, Web3

from common_utils_py.agreements.service_agreement import ServiceAgreement, ServiceTypes
from common_utils_py.ddo.ddo import DDO
from common_utils_py.did import DID
from common_utils_py.metadata import MetadataProvider
from tests.resources.helper_functions import (get_consumer_account, get_ddo_sample, get_ddo_sample2,
                                              get_metadata, get_publisher_account, get_ddo_did_sales_sample,
                                              get_ddo_nft_sample)
from common_utils_py.utils.utilities import generate_prefixed_id


def get_metadata_url():
    if os.getenv('METADATA_URL'):
        return os.getenv('METADATA_URL')
    return 'http://localhost:5000'


def get_keeper_url():
    if os.getenv('KEEPER_URL'):
        return os.getenv('KEEPER_URL')
    return 'http://localhost:8545'


@pytest.fixture(autouse=True)
def setup_all():
    Web3Provider.get_web3('http://localhost:8545')
    ContractHandler.artifacts_path = os.path.expanduser(
        '~/.nevermined/nevermined-contracts/artifacts')
    Keeper.get_instance()


@pytest.fixture
def publisher_account():
    return get_publisher_account()


@pytest.fixture
def consumer_account():
    return get_consumer_account()


@pytest.fixture
def metadata_instance():
    return MetadataProvider.get_metadata_provider(get_metadata_url())


@pytest.fixture
def registered_ddo():
    return DDO()


@pytest.fixture
def web3_instance():
    return Web3(HTTPProvider(get_keeper_url()))


@pytest.fixture
def metadata():
    return get_metadata()


@pytest.fixture
def ddo_sample():
    return get_ddo_sample()


@pytest.fixture
def ddo_sample_2():
    return get_ddo_sample2()


@pytest.fixture
def setup_basic_environment():
    consumer_acc = get_consumer_account()
    publisher_acc = get_publisher_account()
    keeper = Keeper.get_instance()
    return (
        keeper,
        publisher_acc,
        consumer_acc
    )

@pytest.fixture
def setup_agreements_environment():
    consumer_acc = get_consumer_account()
    publisher_acc = get_publisher_account()
    keeper = Keeper.get_instance()

    ddo = get_ddo_sample()

    did_seed = generate_prefixed_id()
    asset_id = keeper.did_registry.hash_did(did_seed, publisher_acc.address)

    ddo._did = DID.did(asset_id)

    keeper.did_registry.register(
        did_seed,
        checksum=Web3Provider.get_web3().toBytes(hexstr=ddo.asset_id),
        url='http://172.17.0.1:5000',
        account=publisher_acc,
        providers=None
    )

    service_agreement = ServiceAgreement.from_ddo(ServiceTypes.ASSET_ACCESS, ddo)
    agreement_id = ServiceAgreement.create_new_agreement_id()
    price = service_agreement.get_price()
    (access_cond_id, lock_cond_id, escrow_cond_id) = service_agreement.generate_agreement_condition_ids(
        agreement_id, asset_id, consumer_acc.address, keeper)

    return (
        keeper,
        ddo,
        publisher_acc,
        consumer_acc,
        agreement_id,
        asset_id,
        price,
        service_agreement,
        (lock_cond_id, access_cond_id, escrow_cond_id),
    )


@pytest.fixture
def setup_did_sales_agreements_environment():
    consumer_acc = get_consumer_account()
    publisher_acc = get_publisher_account()
    keeper = Keeper.get_instance()

    ddo = get_ddo_did_sales_sample()

    did_seed = generate_prefixed_id()
    asset_id = keeper.did_registry.hash_did(did_seed, publisher_acc.address)
    ddo._did = DID.did(asset_id)

    keeper.did_registry.register(
        did_seed,
        checksum=Web3Provider.get_web3().toBytes(hexstr=ddo.asset_id),
        url='metadata:5000',
        account=publisher_acc,
        providers=None
    )

    service_agreement = ServiceAgreement.from_ddo(ServiceTypes.DID_SALES, ddo)
    agreement_id = ServiceAgreement.create_new_agreement_id()
    price = service_agreement.get_price()
    (access_cond_id, lock_cond_id, escrow_cond_id) = service_agreement.generate_agreement_condition_ids(
        agreement_id, asset_id, consumer_acc.address, keeper)

    return (
        keeper,
        ddo,
        publisher_acc,
        consumer_acc,
        agreement_id,
        asset_id,
        price,
        service_agreement,
        (lock_cond_id, access_cond_id, escrow_cond_id),
    )


@pytest.fixture
def setup_nft_sales_agreements_environment():
    consumer_acc = get_consumer_account()
    publisher_acc = get_publisher_account()
    keeper = Keeper.get_instance()

    ddo = get_ddo_nft_sample()

    did_seed = generate_prefixed_id()
    asset_id = keeper.did_registry.hash_did(did_seed, publisher_acc.address)
    ddo._did = DID.did(asset_id)

    keeper.did_registry.register_mintable_did(
        did_seed,
        checksum=Web3Provider.get_web3().toBytes(hexstr=ddo.asset_id),
        url='http://172.17.0.1:5000',
        cap=10,
        royalties=10,
        account=publisher_acc,
        providers=None
    )

    keeper.did_registry.mint(ddo.asset_id, 10, account=publisher_acc)

    service_agreement = ServiceAgreement.from_ddo(ServiceTypes.NFT_SALES, ddo)
    agreement_id = ServiceAgreement.create_new_agreement_id()
    price = service_agreement.get_price()
    (access_cond_id, lock_cond_id, escrow_cond_id) = service_agreement.generate_agreement_condition_ids(
        agreement_id, asset_id, consumer_acc.address, keeper)

    nft_access_service_agreement = ServiceAgreement.from_ddo(ServiceTypes.NFT_ACCESS, ddo)
    nft_access_agreement_id = ServiceAgreement.create_new_agreement_id()

    (nft_access_cond_id, nft_holder_cond_id) = nft_access_service_agreement.generate_agreement_condition_ids(
        nft_access_agreement_id, asset_id, consumer_acc.address, keeper)

    return (
        keeper,
        ddo,
        publisher_acc,
        consumer_acc,
        agreement_id,
        nft_access_agreement_id,
        asset_id,
        price,
        service_agreement,
        nft_access_service_agreement,
        (lock_cond_id, access_cond_id, escrow_cond_id),
        (nft_access_cond_id, nft_holder_cond_id)
    )



# @pytest.fixture
# def setup_agreements_fixed_environment():
#     # agreement_id = '0x9999999999999999999999999999999999999999999999999999999999999999'
#     #agreement_id = '0xeedd99ef65b14f0aa5505f42d2a3150681196c5563ef458c8340808971c50006'
#     agreement_id = ServiceAgreement.create_new_agreement_id()
#     # python ddo
#     #did = 'did:nv:9bc2fb67f4aa56e8c947ffb9af0f3a1a316d2307236134d53a4fb263c44a777d'
#     #did = 'did:nv:8dca838f94414febe3b250268b4455c2041d5de9affb001968f7f6a632bd213f'
#     did = 'did:nv:7d46f1159bc63cd28deb24e34c45b6bf86671c583643ef0a9fb56d8fea767c43'
#     asset_id = '0x' + did.replace('did:nv:', '')
#
#     # consumer_acc = get_consumer_account() # 0x068Ed00cF0441e4829D9784fCBe7b9e26D4BD8d0
#     # consumer_acc = get_account(2) # 0xa99d43d86a0758d5632313b8fa3972b6088a21bb
#     consumer_acc = get_publisher_account() # 0x00bd138abd70e2f00903268f3db08f2d25677c9e
#
#     # publisher_acc = get_publisher_account() # 0x00bd138abd70e2f00903268f3db08f2d25677c9e
#     publisher_acc = get_account(2) # 0xa99d43d86a0758d5632313b8fa3972b6088a21bb
#     keeper = Keeper.get_instance()
#
#     did_resolver = DIDResolver(keeper.did_registry)
#     ddo = did_resolver.resolve(did)
#
#     service_agreement = ServiceAgreement.from_ddo(ServiceTypes.ASSET_ACCESS, ddo)
#     price = service_agreement.get_price()
#     (access_cond_id,
#      lock_cond_id,
#      escrow_cond_id) = service_agreement.generate_agreement_condition_ids(
#         agreement_id, asset_id, consumer_acc.address, publisher_acc.address, keeper
#     )
#     amounts = service_agreement.get_param_value_by_name('_amounts')
#     receivers = service_agreement.get_param_value_by_name('_receivers')
#     return (
#         keeper,
#         ddo,
#         publisher_acc,
#         consumer_acc,
#         agreement_id,
#         asset_id,
#         price,
#         amounts,
#         receivers,
#         service_agreement,
#         (lock_cond_id, access_cond_id, escrow_cond_id),
#     )
