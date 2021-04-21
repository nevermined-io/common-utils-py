from contracts_lib_py.utils import generate_multi_value_hash
from web3 import Web3

from common_utils_py.agreements.service_agreement import ServiceAgreement, ServiceTypes
from common_utils_py.utils.utilities import to_checksum_addresses
from tests.resources.helper_functions import (
    log_event
)


def test_did_sales_flow(setup_did_sales_agreements_environment):
    """Test the DID Sales agreement flow according to the DIDSalesTemplate."""
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

    ) = setup_did_sales_agreements_environment

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

    amounts = service_agreement.get_amounts_int()
    receivers = service_agreement.get_receivers()
    token_address = keeper.token.address

    receiver_0_starting_balance = keeper.token.get_token_balance(
        keeper.agreement_manager.to_checksum_address(receivers[0]))

    assert keeper.template_manager.is_template_approved(
        keeper.did_sales_template.address), 'Template is not approved.'
    assert keeper.did_registry.get_block_number_updated(asset_id) > 0, 'asset id not registered'
    success = keeper.did_sales_template.create_agreement(
        agreement_id,
        asset_id,
        [lock_cond_id, access_cond_id, escrow_cond_id],
        service_agreement.conditions_timelocks,
        service_agreement.conditions_timeouts,
        consumer_acc.address,
        publisher_acc
    )
    print('create agreement: ', success)
    assert success, f'createAgreement failed {success}'
    event = keeper.did_sales_template.subscribe_agreement_created(
        agreement_id,
        10,
        log_event(keeper.did_sales_template.AGREEMENT_CREATED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for AgreementCreated '

    # Verify condition types (condition contracts)
    agreement = keeper.agreement_manager.get_agreement(agreement_id)
    assert agreement.did == asset_id, ''
    cond_types = keeper.did_sales_template.get_condition_types()
    for i, cond_id in enumerate(agreement.condition_ids):
        cond = keeper.condition_manager.get_condition(cond_id)
        assert cond.type_ref == cond_types[i]
        assert int(cond.state) == 1

    # Give consumer some tokens
    keeper.dispenser.request_vodkas(price, consumer_acc)

    # Fulfill lock_payment_condition
    pub_token_balance = keeper.token.get_token_balance(publisher_acc.address)
    consumer_token_balance = keeper.token.get_token_balance(consumer_acc.address)
    assert consumer_token_balance >= price, 'Consumer doesnt have enough tokens to afford the purchase'

    starting_balance = keeper.token.get_token_balance(keeper.escrow_payment_condition.address)
    keeper.token.token_approve(keeper.lock_payment_condition.address, price, consumer_acc)
    tx_hash = keeper.lock_payment_condition.fulfill(
        agreement_id, asset_id, keeper.escrow_payment_condition.address, token_address, amounts, receivers, consumer_acc)
    keeper.lock_payment_condition.get_tx_receipt(tx_hash)
    event = keeper.lock_payment_condition.subscribe_condition_fulfilled(
        agreement_id,
        10,
        log_event(keeper.lock_payment_condition.FULFILLED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for LockPaymentCondition.Fulfilled'
    assert keeper.condition_manager.get_condition_state(lock_cond_id) == 2, ''
    assert keeper.token.get_token_balance(
        keeper.escrow_payment_condition.address
    ) == (price + starting_balance), ''

    # Fulfill transfer did condition
    tx_hash = keeper.transfer_did_condition.fulfill(
        agreement_id, asset_id, consumer_acc.address, publisher_acc
    )
    keeper.transfer_did_condition.get_tx_receipt(tx_hash)
    event = keeper.transfer_did_condition.subscribe_condition_fulfilled(
        agreement_id,
        20,
        log_event(keeper.transfer_did_condition.FULFILLED_EVENT),
        (),
        wait=True
    )
    assert event, 'no event for TransferDIDOwnershipCondition.Fulfilled'
    assert keeper.condition_manager.get_condition_state(access_cond_id) == 2, ''

    # Fulfill escrow_payment_condition
    tx_hash = keeper.escrow_payment_condition.fulfill(
        agreement_id, asset_id, amounts, receivers,
        keeper.escrow_payment_condition.address, token_address, lock_cond_id,
        access_cond_id, publisher_acc
    )

    keeper.escrow_payment_condition.get_tx_receipt(tx_hash)
    event = keeper.escrow_payment_condition.subscribe_condition_fulfilled(
        agreement_id,
        10,
        log_event(keeper.escrow_payment_condition.FULFILLED_EVENT),
        (),
        wait=True
    )

    assert event, 'no event for EscrowPayment.Fulfilled'
    assert keeper.condition_manager.get_condition_state(escrow_cond_id) == 2, ''
    assert keeper.token.get_token_balance(
        keeper.escrow_payment_condition.address
    ) == starting_balance, ''

    assert keeper.token.get_token_balance(
        keeper.agreement_manager.to_checksum_address(receivers[0])) == (receiver_0_starting_balance + int(amounts[0])), ''


