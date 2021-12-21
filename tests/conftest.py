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
def json_service():
    return {"type":"nft-sales","index":6,"serviceEndpoint":"https://gateway.rinkeby.nevermined.rocks/api/v1/gateway/services/nft","templateId":"0x24edffc52926739E8403E451b791378349f38818","attributes":{"main":{"name":"nftSalesAgreement","creator":"0xD0064bD1a8DD5a3F775A5432f833EaC9f21CcA80","datePublished":"2021-11-23T10:27:07Z","timeout":86400},"additionalInformation":{"description":""},"serviceAgreementTemplate":{"contractName":"NFTSalesTemplate","events":[{"name":"AgreementCreated","actorType":"consumer","handler":{"moduleName":"nftSalesTemplate","functionName":"fulfillLockPaymentCondition","version":"0.1"}}],"fulfillmentOrder":["lockPayment.fulfill","transferNFT.fulfill","escrowPayment.fulfill"],"conditionDependency":{"lockPayment":[],"transferNFT":[],"escrowPayment":["lockPayment","transferNFT"]},"conditions":[{"name":"lockPayment","timelock":0,"timeout":0,"contractName":"LockPaymentCondition","functionName":"fulfill","parameters":[{"name":"_did","type":"bytes32","value":"688190baee42efb665fb45799135f1511256839e84ccfa7b48616839c49fd427"},{"name":"_rewardAddress","type":"address","value":"0xD0064bD1a8DD5a3F775A5432f833EaC9f21CcA80"},{"name":"_tokenAddress","type":"address","value":"0x937Cc2ec24871eA547F79BE8b47cd88C0958Cc4D"},{"name":"_amounts","type":"uint256[]","value":["20"]},{"name":"_receivers","type":"address[]","value":["0xD0064bD1a8DD5a3F775A5432f833EaC9f21CcA80"]}]}]}}}


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