import os

import pytest
from contracts_lib_py.contract_handler import ContractHandler
from contracts_lib_py.keeper import Keeper
from contracts_lib_py.web3_provider import Web3Provider
from web3 import HTTPProvider, Web3

from common_utils_py.agreements.service_agreement import ServiceAgreement, ServiceTypes
from common_utils_py.ddo.ddo import DDO
from common_utils_py.did import DID
from common_utils_py.metadata import MetadataProvider
from tests.resources.helper_functions import (get_consumer_account, get_ddo_sample, get_ddo_sample2,
                                              get_metadata, get_publisher_account)


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
def setup_agreements_environment():
    consumer_acc = get_consumer_account()
    publisher_acc = get_publisher_account()
    keeper = Keeper.get_instance()

    ddo = get_ddo_sample()
    ddo._did = DID.did({"0": "0x12341234"})
    keeper.did_registry.register(
        ddo.asset_id,
        checksum=Web3Provider.get_web3().toBytes(hexstr=ddo.asset_id),
        url='metadata:5000',
        account=publisher_acc,
        providers=None
    )

    registered_ddo = ddo
    asset_id = registered_ddo.asset_id
    service_agreement = ServiceAgreement.from_ddo(ServiceTypes.ASSET_ACCESS, ddo)
    agreement_id = ServiceAgreement.create_new_agreement_id()
    price = service_agreement.get_price()
    (access_cond_id,
     lock_cond_id,
     escrow_cond_id) = service_agreement.generate_agreement_condition_ids(
        agreement_id, asset_id, consumer_acc.address, publisher_acc.address, keeper
    )

    return (
        keeper,
        publisher_acc,
        consumer_acc,
        agreement_id,
        asset_id,
        price,
        service_agreement,
        (lock_cond_id, access_cond_id, escrow_cond_id),
    )
