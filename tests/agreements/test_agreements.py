import pytest
from contracts_lib_py import Keeper
from contracts_lib_py.utils import generate_multi_value_hash
from web3 import Web3

from common_utils_py.agreements.service_agreement import ServiceAgreement, ServiceTypes
from common_utils_py.utils.utilities import to_checksum_addresses
from tests.resources.helper_functions import (
    log_event
)



def test_escrow_access_secret_store_template_flow(setup_agreements_environment):
    """Test the agreement flow according to the EscrowAccessSecretStoreTemplate."""
    (
        keeper,
        ddo,
        publisher_acc,
        consumer_acc,
        agreement_id,
        asset_id,
        price,
        service_agreement,
        (lock_cond_id, access_cond_id, escrow_cond_id),

    ) = setup_agreements_environment

    print('creating agreement:'
          'agrId: ', agreement_id,
          'asset_id', asset_id,
          '[lock_cond_id, access_cond_id, escrow_cond_id]',
          [lock_cond_id, access_cond_id, escrow_cond_id],
          'tlocks', service_agreement.conditions_timelocks,
          'touts', service_agreement.conditions_timeouts,
          'consumer', consumer_acc.address,
          'publisher', publisher_acc.address
          )

    amounts = service_agreement.get_param_value_by_name('_amounts')
    receivers = service_agreement.get_param_value_by_name('_receivers')

    receiver_0_starting_balance = keeper.token.get_token_balance(
        keeper.agreement_manager.to_checksum_address(receivers[0]))

    assert keeper.template_manager.is_template_approved(
        keeper.escrow_access_secretstore_template.address), 'Template is not approved.'
    assert keeper.did_registry.get_block_number_updated(asset_id) > 0, 'asset id not registered'
    success = keeper.escrow_access_secretstore_template.create_agreement(
        agreement_id,
        asset_id,
        [access_cond_id, lock_cond_id, escrow_cond_id],
        service_agreement.conditions_timelocks,
        service_agreement.conditions_timeouts,
        consumer_acc.address,
        publisher_acc
    )
    print('create agreement: ', success)
    assert success, f'createAgreement failed {success}'
    event = keeper.escrow_access_secretstore_template.subscribe_agreement_created(
        agreement_id,
        10,
        log_event(keeper.escrow_access_secretstore_template.AGREEMENT_CREATED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for AgreementCreated '

    # Verify condition types (condition contracts)
    agreement = keeper.agreement_manager.get_agreement(agreement_id)
    assert agreement.did == asset_id, ''
    cond_types = keeper.escrow_access_secretstore_template.get_condition_types()
    for i, cond_id in enumerate(agreement.condition_ids):
        cond = keeper.condition_manager.get_condition(cond_id)
        assert cond.type_ref == cond_types[i]
        assert int(cond.state) == 1

    # Give consumer some tokens
    keeper.dispenser.request_vodkas(price, consumer_acc)

    # Fulfill lock_reward_condition
    pub_token_balance = keeper.token.get_token_balance(publisher_acc.address)
    starting_balance = keeper.token.get_token_balance(keeper.escrow_reward_condition.address)
    keeper.token.token_approve(keeper.lock_reward_condition.address, price, consumer_acc)
    tx_hash = keeper.lock_reward_condition.fulfill(
        agreement_id, keeper.escrow_reward_condition.address, price, consumer_acc)
    keeper.lock_reward_condition.get_tx_receipt(tx_hash)
    event = keeper.lock_reward_condition.subscribe_condition_fulfilled(
        agreement_id,
        10,
        log_event(keeper.lock_reward_condition.FULFILLED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for LockRewardCondition.Fulfilled'
    assert keeper.condition_manager.get_condition_state(lock_cond_id) == 2, ''
    assert keeper.token.get_token_balance(
        keeper.escrow_reward_condition.address
    ) == (price + starting_balance), ''

    # Fulfill access_secret_store_condition
    tx_hash = keeper.access_secret_store_condition.fulfill(
        agreement_id, asset_id, consumer_acc.address, publisher_acc
    )
    keeper.access_secret_store_condition.get_tx_receipt(tx_hash)
    event = keeper.access_secret_store_condition.subscribe_condition_fulfilled(
        agreement_id,
        20,
        log_event(keeper.access_secret_store_condition.FULFILLED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for AccessSecretStoreCondition.Fulfilled'
    assert keeper.condition_manager.get_condition_state(access_cond_id) == 2, ''

    checksum_addresses = to_checksum_addresses(receivers)

    # Fulfill escrow_reward_condition
    tx_hash = keeper.escrow_reward_condition.fulfill(
        agreement_id, amounts, checksum_addresses,
        publisher_acc.address, lock_cond_id,
        access_cond_id, publisher_acc
    )
    keeper.escrow_reward_condition.get_tx_receipt(tx_hash)
    event = keeper.escrow_reward_condition.subscribe_condition_fulfilled(
        agreement_id,
        10,
        log_event(keeper.escrow_reward_condition.FULFILLED_EVENT),
        (),
        wait=True
    )

    assert event, 'no event for EscrowReward.Fulfilled'
    assert keeper.condition_manager.get_condition_state(escrow_cond_id) == 2, ''
    assert keeper.token.get_token_balance(
        keeper.escrow_reward_condition.address
    ) == starting_balance, ''

    assert keeper.token.get_token_balance(
        keeper.agreement_manager.to_checksum_address(receivers[0])) == (receiver_0_starting_balance + amounts[0]), ''


def test_agreement_hash(ddo_sample):
    """
    This test verifies generating agreement hash using fixed inputs and ddo example.
    This will make it easier to compare the hash generated from different languages.
    """
    w3 = Web3
    did = "did:nv:0c184915b07b44c888d468be85a9b28253e80070e5294b1aaed81c2f0264e430"
    template_id = w3.toChecksumAddress("0x00bd138abd70e2f00903268f3db08f2d25677c9e")
    agreement_id = '0xf136d6fadecb48fdb2fc1fb420f5a5d1c32d22d9424e47ab9461556e058fefaa'
    sa = ServiceAgreement.from_service_dict(
        ddo_sample.get_service(ServiceTypes.ASSET_ACCESS).as_dictionary())
    sa.service_agreement_template.set_template_id(template_id)
    assert template_id == sa.template_id, ''
    assert did == ddo_sample.did
    # Don't generate condition ids, use fixed ids so we get consistent hash
    # (access_id, lock_id, escrow_id) = sa.generate_agreement_condition_ids(
    #     agreement_id, ddo.asset_id, consumer, publisher, keeper)
    access_id = '0x2d7c1d60dc0c3f52aa9bd71ffdbe434a0e58435571e64c893bc9646fea7f6ec1'
    lock_id = '0x1e265c434c14e668695dda1555088f0ea4356f596bdecb8058812e7dcba9ee73'
    escrow_id = '0xe487fa6d435c2f09ef14b65b34521302f1532ac82ba8f6c86116acd8566e2da3'
    print(f'condition ids: \n'
          f'{access_id} \n'
          f'{lock_id} \n'
          f'{escrow_id}')
    agreement_hash = ServiceAgreement.generate_service_agreement_hash(
        sa.template_id,
        (access_id, lock_id, escrow_id),
        sa.conditions_timelocks,
        sa.conditions_timeouts,
        agreement_id,
        generate_multi_value_hash
    )
    print('agreement hash: ', agreement_hash.hex())
    expected = '0x96732b390dacec0f19ad304ac176b3407968a0184d01b3262687fd23a3f0995e'
    print('expected hash: ', expected)
    assert agreement_hash.hex() == expected, 'hash does not match.'

# THIS TEST IS ONLY VALID FOR SIMULATING HASH ENCODINGS IN A FIXED ENVIRONMENT
# USEFUL TO VALIDATE DIFFERENCES BETWEEN PARAMETER ENCODING BETWEEN SDK IMPLEMENTATIONS
#
# def test_escrow_reward_condition_id(setup_agreements_fixed_environment):
#     """Test the escrow reward condition id"""
#
#
#     (
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
#
#     ) = setup_agreements_fixed_environment
#
#     checksum_addresses = to_checksum_addresses(receivers)
#
#     # Give consumer some tokens
#     keeper.dispenser.request_vodkas(price, consumer_acc)
#
#     (access_cond_id,
#      lock_cond_id,
#      escrow_cond_id) = service_agreement.generate_agreement_condition_ids(
#         agreement_id, asset_id, consumer_acc.address, publisher_acc.address, keeper
#     )
#     escrow_cond_id_generated = keeper.escrow_reward_condition.generate_id(
#         agreement_id,
#         service_agreement.condition_by_name['escrowReward'].param_types,
#         [amounts, checksum_addresses, publisher_acc.address, lock_cond_id, access_cond_id]
#     ).hex()
#
#     assert escrow_cond_id == escrow_cond_id_generated
#
#     success = keeper.escrow_access_secretstore_template.create_agreement(
#         agreement_id,
#         asset_id,
#         [access_cond_id, lock_cond_id, escrow_cond_id],
#         service_agreement.conditions_timelocks,
#         service_agreement.conditions_timeouts,
#         consumer_acc.address,
#         consumer_acc
#     )
#     print('create agreement: ', success)
#     assert success, f'createAgreement failed {success}'
#     event = keeper.escrow_access_secretstore_template.subscribe_agreement_created(
#         agreement_id,
#         10,
#         log_event(keeper.escrow_access_secretstore_template.AGREEMENT_CREATED_EVENT),
#         (),
#         wait=True
#     )
#     assert event, 'no event for AgreementCreated '
#
#     # Verify condition types (condition contracts)
#     agreement = keeper.agreement_manager.get_agreement(agreement_id)
#     assert agreement.did == asset_id, ''
#     cond_types = keeper.escrow_access_secretstore_template.get_condition_types()
#     for i, cond_id in enumerate(agreement.condition_ids):
#         cond = keeper.condition_manager.get_condition(cond_id)
#         assert cond.type_ref == cond_types[i]
#         assert int(cond.state) == 1
#
#     # Give consumer some tokens
#     keeper.dispenser.request_vodkas(price, consumer_acc)
#
#     # Fulfill lock_reward_condition
#     pub_token_balance = keeper.token.get_token_balance(publisher_acc.address)
#     starting_balance = keeper.token.get_token_balance(keeper.escrow_reward_condition.address)
#     keeper.token.token_approve(keeper.lock_reward_condition.address, price, consumer_acc)
#     tx_hash = keeper.lock_reward_condition.fulfill(
#         agreement_id, keeper.escrow_reward_condition.address, price, consumer_acc)
#     keeper.lock_reward_condition.get_tx_receipt(tx_hash)
#     event = keeper.lock_reward_condition.subscribe_condition_fulfilled(
#         agreement_id,
#         10,
#         log_event(keeper.lock_reward_condition.FULFILLED_EVENT),
#         (),
#         wait=True
#     )
#     assert event, 'no event for LockRewardCondition.Fulfilled'
#     assert keeper.condition_manager.get_condition_state(lock_cond_id) == 2, ''
#     assert keeper.token.get_token_balance(
#         keeper.escrow_reward_condition.address
#     ) == (price + starting_balance), ''
#
#     # Fulfill access_secret_store_condition
#     tx_hash = keeper.access_secret_store_condition.fulfill(
#         agreement_id, asset_id, consumer_acc.address, publisher_acc
#     )
#     keeper.access_secret_store_condition.get_tx_receipt(tx_hash)
#     event = keeper.access_secret_store_condition.subscribe_condition_fulfilled(
#         agreement_id,
#         20,
#         log_event(keeper.access_secret_store_condition.FULFILLED_EVENT),
#         (),
#         wait=True
#     )
#     assert event, 'no event for AccessSecretStoreCondition.Fulfilled'
#     assert keeper.condition_manager.get_condition_state(access_cond_id) == 2, ''
#
#
#     # Fulfill escrow_reward_condition
#     tx_hash = keeper.escrow_reward_condition.fulfill(
#         agreement_id, amounts, checksum_addresses,
#         publisher_acc.address, lock_cond_id,
#         access_cond_id, publisher_acc
#     )
#     keeper.escrow_reward_condition.get_tx_receipt(tx_hash)
#     assert keeper.condition_manager.get_condition_state(escrow_cond_id) == 2, ''
#
#     print('agreementId: ' + agreement_id)
#     print('did: ' + asset_id)
#     print('lockConditionId: ' + lock_cond_id)
#     print('accessConditionId: ' + access_cond_id)
#     print('escrowConditionId: ' + escrow_cond_id)
#     print('publisherAccount: ' + publisher_acc.address)
#     print('consumerAccount: ' + consumer_acc.address)


def test_agreement():
    template_id = Web3.toChecksumAddress('0x' + ('f' * 40))
    agreement_id = '0x' + ('e' * 64)
    access_id = '0x' + ('a' * 64)
    lock_id = '0x' + ('b' * 64)
    escrow_id = '0x' + ('c' * 64)

    signature = ServiceAgreement.generate_service_agreement_hash(
        template_id,
        [access_id, lock_id, escrow_id],
        [0, 0, 0],
        [0, 0, 0],
        agreement_id,
        generate_multi_value_hash
    )

    print({signature})
    assert (
            signature == Web3.toBytes(
        hexstr="0x67901517c18a3d23e05806fff7f04235cc8ae3b1f82345b8bfb3e4b02b5800c7"
    )), "The signature is not correct."
