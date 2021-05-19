"""
    Test did_lib
"""

import pytest
from contracts_lib_py import Keeper

from common_utils_py.agreements.service_agreement import ServiceTypes
from common_utils_py.ddo.ddo import DDO
from common_utils_py.ddo.public_key_base import PublicKeyBase
from common_utils_py.ddo.public_key_rsa import PUBLIC_KEY_TYPE_ETHEREUM_ECDSA, PUBLIC_KEY_TYPE_RSA
from common_utils_py.did import DID, did_to_id_bytes
from common_utils_py.utils.utilities import checksum
from tests.resources.helper_functions import get_publisher_account

TEST_SERVICE_TYPE = 'ocean-meta-storage'
TEST_SERVICE_URL = 'http://localhost:8005'


def test_create_ddo(metadata):
    pub_acc = get_publisher_account()
    ddo = DDO()
    ddo.add_service(ServiceTypes.METADATA, 'http://mymetadata.com',
                    values=dict({"attributes": metadata}), index='0')
    checksums = dict()
    for service in ddo.services:
        checksums[str(service.index)] = checksum(service.main)
    ddo.add_proof(checksums, pub_acc)
    did = ddo.assign_did(DID.encoded_did(ddo.proof['checksum']))
    ddo.proof['signatureValue'] = Keeper.sign_hash(did_to_id_bytes(did), pub_acc)
    ddo.add_public_key(did, pub_acc.address)
    ddo.add_authentication(did, PUBLIC_KEY_TYPE_RSA)


def test_creating_ddo_from_scratch():
    # create an empty ddo
    ddo = DDO()
    assert ddo.did is None
    assert ddo.asset_id is None
    assert ddo.created is not None

    did = DID.did("0x99999999999999999")
    ddo.assign_did(did)
    assert ddo.did == did

    pub_acc = get_publisher_account()

    ddo.add_service(TEST_SERVICE_TYPE, TEST_SERVICE_URL)

    # add a proof to the first public_key/authentication
    ddo.add_proof('checksum', pub_acc)
    ddo_text_proof = ddo.as_text()
    assert ddo_text_proof

    pub_acc = get_publisher_account()
    assert not ddo.public_keys
    ddo.add_public_key(did, pub_acc.address)
    assert len(ddo.public_keys) == 1
    assert ddo.get_public_key(0) == ddo.public_keys[0]
    with pytest.raises(IndexError):
        ddo.get_public_key(1)

    assert ddo.get_public_key(did) == ddo.public_keys[0]
    assert ddo.get_public_key('0x32233') is None

    assert not ddo.authentications
    ddo.add_authentication(did, '')
    assert len(ddo.authentications) == 1


def test_create_auth_from_json():
    auth = {'publicKey': '0x00000', 'type': 'auth-type', 'nothing': ''}
    assert (
            DDO.create_authentication_from_json(auth)
            ==
            {'publicKey': '0x00000', 'type': 'auth-type'}
    )
    with pytest.raises(ValueError):
        DDO.create_authentication_from_json({'type': 'auth-type'})


def test_create_public_key_from_json():
    pkey = {'id': 'pkeyid', 'type': 'keytype', 'owner': '0x00009'}
    pub_key_inst = DDO.create_public_key_from_json(pkey)
    assert isinstance(pub_key_inst, PublicKeyBase)
    assert pub_key_inst.get_id() == pkey['id']
    assert pub_key_inst.get_type() == PUBLIC_KEY_TYPE_ETHEREUM_ECDSA
    assert pub_key_inst.get_owner() == pkey['owner']

    pub_key_inst = DDO.create_public_key_from_json(
        {'type': PUBLIC_KEY_TYPE_RSA}
    )
    assert pub_key_inst.get_id() == ''
    assert pub_key_inst.get_type() == PUBLIC_KEY_TYPE_RSA
    assert pub_key_inst.get_owner() is None


def test_load_ddo_json(ddo_sample_2):
    service = ddo_sample_2.get_service(ServiceTypes.METADATA)
    assert service
    assert service.type == ServiceTypes.METADATA
    assert service.attributes


def test_ddo_dict(ddo_sample_2):
    assert len(ddo_sample_2.public_keys) == 1
    assert ddo_sample_2.did == \
           'did:nv:0c184915b07b44c888d468be85a9b28253e80070e5294b1aaed81c2f0264e431'


def test_find_service(ddo_sample):
    service = ddo_sample.get_service_by_index(0)
    assert service and service.type == ServiceTypes.METADATA, 'Failed to find service by integer ' \
                                                              'id.'
    service = ddo_sample.get_service_by_index('0')
    assert service and service.type == ServiceTypes.METADATA, 'Failed to find service by str(int)' \
                                                              ' id.'

    service = ddo_sample.get_service_by_index(3)
    assert service and service.type == ServiceTypes.ASSET_ACCESS, 'Failed to find service by ' \
                                                                  'integer id.'
    service = ddo_sample.get_service_by_index('3')
    assert service and service.type == ServiceTypes.ASSET_ACCESS, 'Failed to find service by str(' \
                                                                  'int) id.'

    service = ddo_sample.get_service(ServiceTypes.ASSET_ACCESS)
    assert service and service.type == ServiceTypes.ASSET_ACCESS, 'Failed to find service by id ' \
                                                                  'using service type.'
    assert service.index == 3, 'index not as expected.'

    service = ddo_sample.get_service(ServiceTypes.METADATA)
    assert service and service.type == ServiceTypes.METADATA, 'Failed to find service by id using ' \
                                                              '' \
                                                              '' \
                                                              'service ' \
                                                              'type.'
    assert service.index == 0, 'index not as expected.'
