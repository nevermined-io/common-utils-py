def test_encoding(setup_basic_environment):
    """Test the agreement flow according to the AccessTemplate."""
    (
        keeper,
        publisher_acc,
        consumer_acc,
    ) = setup_basic_environment

    agreement_id = '0x6098b775850142a1bd13ceca600a1dfad5c58aae6cd8499c9f02c0cf1e052a17'
    token_address = '0x80163Dec819063F87ad4F1b6A24DA551C93c5777'
    amounts = [10, 2]
    receivers = ['0x00Bd138aBD70e2F00903268F3Db08f2D25677C9e', '0x068Ed00cF0441e4829D9784fCBe7b9e26D4BD8d0']
    asset_id = '0x0792cbe4ea0285a2a2db26f262c44b7478e02dc3da380f7c54be1634300b86b7'
    escrow_condition_address = '0x602e6AA9Ea3293410B6103283cE109E2073FC160'

    _contract_lock_hash = '0x' + keeper.lock_payment_condition.hash_values(asset_id, escrow_condition_address, token_address, amounts, receivers).hex()
    assert _contract_lock_hash == '0x20d5d330cad3f7d6769da69ac3f569676c83db2c27e750e0c65c43be359b059c'

    _contract_lock_hash_2 = '0x' + keeper.lock_payment_condition.contract.functions.hashValues(asset_id, escrow_condition_address, token_address, amounts, receivers).call().hex()
    assert _contract_lock_hash == _contract_lock_hash_2

    _id = '0x' + keeper.lock_payment_condition.contract.functions.generateId(agreement_id, _contract_lock_hash).call().hex()

    assert _id != _contract_lock_hash
