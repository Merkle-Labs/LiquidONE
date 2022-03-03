import pytest
from brownie import accounts, stONE, oneLidoNFT, Contract, network, exceptions
from scripts.helper_functions import *
from utils.constants import *
from time import sleep
from random import random


@pytest.fixture( scope = "module", autouse = True )
def setup():
    pass


def test_simple_staking():
    print( "Initiating staking contract with one validator..." )
    print(
        "Creating the validator at {} using the Harmony SDK"
        .format( validator_address )
    )
    load_wallets()
    create_validator(
        validator_address,
        validator_info,
        accounts[ 0 ].private_key
    )
    sone_contract, lone_contract = deploy_from_address( accounts[ 0 ] )
    while sone_contract._epoch() < 2:
        countdown( 5 )
    inputx = amount * 2
    stake_tx = stake( inputx, sone_contract, lone_contract, accounts[ 0 ] )
    expectedOutput = inputx
    delegation_by_delegator = staking.get_delegation_by_delegator_and_validator(
        sone_contract.address,
        validator_address,
        test_net
    )
    total_delegation = staking.get_delegations_by_validator(
        validator_address,
        test_net
    )
    print( "-" * 50 )
    assert ( sone_contract.balanceOf( accounts[ 0 ] ) == expectedOutput )
    assert ( delegation_by_delegator[ 'amount' ] == expectedOutput )
    assert (
        convert_one_to_hex( delegation_by_delegator[ 'delegator_address' ]
                           ) == sone_contract.address
    )
    assert ( delegation_by_delegator[ 'amount' ] == expectedOutput )


def test_staking_should_fail_minimum_delegation():
    print( "Initiating staking contract with one validator..." )
    print(
        "Creating the validator at {} using the Harmony SDK"
        .format( validator_address )
    )
    load_wallets()
    create_validator(
        validator_address,
        validator_info,
        accounts[ 0 ].private_key
    )
    stone_contract, lone_contract = deploy()
    while stone_contract._epoch() < 2:
        countdown( 10 )
    input = amount - 1  # sending 99 one for delegation
    with pytest.raises(
        ValueError
    ):  # Brownie should raise an error instead of pytest
        stake_tx = stake(
            input,
            stone_contract,
            lone_contract,
            accounts[ 0 ].address
        )


def test_staking_checking_multiple_validator_balances():
    print( "Initiating staking contract with one validator..." )
    print(
        "Creating the validator at {} using the Harmony SDK"
        .format( validator_address )
    )
    load_wallets()
    create_validator(
        validator_address,
        validator_info,
        accounts[ 0 ].private_key
    )
    create_spare_validators()
    stone_contract, lone_contract = deploy_with_3_validators()
    validators = [
        validator_address,
        spare_validators[ 0 ],
        spare_validators[ 1 ]
    ]
    while stone_contract._epoch() < 2:
        countdown( 10 )
    input = amount * 12
    stake_tx = stake(
        input,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )
    expectedOutput = [
        input * 3333 / 10000,
        input * 3333 / 10000,
        input * 3334 / 10000
    ]
    for index, validator in enumerate( validators ):
        delegation_by_validator = staking.get_delegation_by_delegator_and_validator(
            stone_contract.address,
            validator,
            test_net
        )
        assert (
            delegation_by_validator[ 'amount' ] == expectedOutput[ index ]
        )


def test_staking_multiple_validator_with_inadequate_balance():
    print( "Initiating staking contract with one validator..." )
    print(
        "Creating the validator at {} using the Harmony SDK"
        .format( validator_address )
    )
    load_wallets()
    create_validator(
        validator_address,
        validator_info,
        accounts[ 0 ].private_key
    )
    create_spare_validators()
    stone_contract, lone_contract = deploy_with_3_validators()
    validators = [
        validator_address,
        spare_validators[ 0 ],
        spare_validators[ 1 ]
    ]
    while stone_contract._epoch() < 2:
        countdown( 10 )
    input = amount * 3
    stake_tx = stake(
        input,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )
    expectedOutput = [ None, None, input * 3334 / 10000 ]
    for index, validator in enumerate( validators ):
        delegation_by_validator = staking.get_delegation_by_delegator_and_validator(
            stone_contract.address,
            validator,
            test_net
        )
        delegation_amount_by_validator = delegation_by_validator if delegation_by_validator != None else {}
        assert (
            delegation_amount_by_validator.get( 'amount',
                                                None ) ==
            expectedOutput[ index ]
        )
    assert ( stone_contract.balance() == ( input - input * 3334 / 10000 ) )
    assert (
        stone_contract.totalAccruedPendingDelegations() == input -
        input * 3334 / 10000
    )


def test_staking_complex_multiple_validator_accounts():
    print( "Initiating staking contract with one validator..." )
    print(
        "Creating the validator at {} using the Harmony SDK"
        .format( validator_address )
    )
    load_wallets()
    create_validator(
        validator_address,
        validator_info,
        accounts[ 0 ].private_key
    )
    create_spare_validators()
    stone_contract, lone_contract = deploy_with_3_validators()
    validators = [
        validator_address,
        spare_validators[ 0 ],
        spare_validators[ 1 ]
    ]
    while stone_contract._epoch() < 2:
        countdown( 10 )
    input = amount * 3
    stake_tx = stake( input, stone_contract, lone_contract, accounts[ 1 ] )
    expectedOutput = [ None, None, input * 3334 / 10000 ]
    expectedPendingDelegation = [
        input * 3333 / 10000,
        input * 3333 / 10000,
        0
    ]
    for index, validator in enumerate( validators ):
        delegation_by_validator = staking.get_delegation_by_delegator_and_validator(
            stone_contract.address,
            validator,
            test_net
        )
        delegation_amount_by_validator = delegation_by_validator if delegation_by_validator != None else {}
        assert (
            delegation_amount_by_validator.get( 'amount',
                                                None ) ==
            expectedOutput[ index ]
        )
        print( "...............Index..................", index )
        assert (
            stone_contract.accruedPendingDelegations(
                convert_one_to_hex( validators[ index ] )
            ) == expectedPendingDelegation[ index ]
        )
    assert ( stone_contract.balance() == ( input - input * 3334 / 10000 ) )
    assert (
        stone_contract.totalAccruedPendingDelegations() == input -
        input * 3334 / 10000
    )
    assert ( stone_contract.totalClaimableBalance() == 0 )

    stake_tx2 = stake(
        amount,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )
    expectedOutput2 = [
        amount * 4 * 3333 / 10000,
        amount * 4 * 3333 / 10000,
        amount * 3 * 3334 / 10000
    ]
    expectedPendingDelegation2 = [ 0, 0, amount * 3334 / 10000 ]
    for index, validator in enumerate( validators ):
        delegation_by_validator = staking.get_delegation_by_delegator_and_validator(
            stone_contract.address,
            validator,
            test_net
        )
        delegation_amount_by_validator = delegation_by_validator if delegation_by_validator != None else {}
        assert (
            delegation_amount_by_validator.get( 'amount',
                                                None ) ==
            expectedOutput2[ index ]
        )
        assert (
            stone_contract.accruedPendingDelegations(
                convert_one_to_hex( validators[ index ] )
            ) == expectedPendingDelegation2[ index ]
        )
    assert ( stone_contract.balance() == ( amount * 3334 / 10000 ) )
    assert (
        stone_contract.totalAccruedPendingDelegations() == amount * 3334 / 10000
    )
    assert ( stone_contract.balanceOf( accounts[ 0 ] ) == amount )
    assert ( stone_contract.balanceOf( accounts[ 1 ] ) == amount * 3 )
    assert ( stone_contract.totalClaimableBalance() == 0 )

    stake_tx3 = stake(
        amount * 2,
        stone_contract,
        lone_contract,
        accounts[ 1 ]
    )
    # print('Validator1....', stone_contract.validatorStakedAmount(stone_contract.validatorAddresses(0)))
    # print('Validator2....', stone_contract.validatorStakedAmount(stone_contract.validatorAddresses(1)))
    # print('Validator3....', stone_contract.validatorStakedAmount(stone_contract.validatorAddresses(2)))
    expectedOutput3 = [
        amount * 4 * 3333 / 10000,
        amount * 4 * 3333 / 10000,
        amount * 3 * 3334 / 10000 + amount * ( 1 + 2 ) * 3334 / 10000
    ]
    expectedPendingDelegation3 = [
        amount * 2 * 3333 / 10000,
        amount * 2 * 3333 / 10000,
        0
    ]
    for index, validator in enumerate( validators ):
        delegation_by_validator = staking.get_delegation_by_delegator_and_validator(
            stone_contract.address,
            validator,
            test_net
        )
        delegation_amount_by_validator = delegation_by_validator if delegation_by_validator != None else {}
        assert (
            delegation_amount_by_validator.get( 'amount',
                                                None ) ==
            expectedOutput3[ index ]
        )
        assert (
            stone_contract.accruedPendingDelegations(
                convert_one_to_hex( validators[ index ] )
            ) == expectedPendingDelegation3[ index ]
        )
    assert ( stone_contract.balance() == ( amount * 4 * 3333 / 10000 ) )
    assert (
        stone_contract.totalAccruedPendingDelegations() == amount * 4 * 3333 /
        10000
    )
    assert ( stone_contract.balanceOf( accounts[ 0 ] ) == amount )
    assert ( stone_contract.balanceOf( accounts[ 1 ] ) == amount * 5 )
    assert ( stone_contract.totalClaimableBalance() == 0 )
    # assert(stone_contract.balanceOf(three) == amount*2)

    unstake_tx3 = unstake(
        amount,
        stone_contract,
        lone_contract,
        accounts[ 0 ]
    )
    # unstake_tx4 = unstake(amount*1.5, stone_contract, lone_contract, three)
    unstake_tx5 = unstake(
        amount * 3,
        stone_contract,
        lone_contract,
        accounts[ 1 ]
    )

    expectedOutput4 = [
        amount * 2 * 3333 / 10000,
        amount * 2 * 3333 / 10000,
        amount * 2 * 3334 / 10000
    ]
    expectedPendingDelegation4 = [ 0, 0, 0 ]
    for index, validator in enumerate( validators ):
        delegation_by_validator = staking.get_delegation_by_delegator_and_validator(
            stone_contract.address,
            validator,
            test_net
        )
        delegation_amount_by_validator = delegation_by_validator if delegation_by_validator != None else {}
        assert (
            delegation_amount_by_validator.get( 'amount',
                                                None ) ==
            expectedOutput4[ index ]
        )
        assert (
            stone_contract.accruedPendingDelegations(
                convert_one_to_hex( validators[ index ] )
            ) == expectedPendingDelegation4[ index ]
        )
    assert ( stone_contract.balance() == ( amount * 4 * 3333 / 10000 ) )
    assert ( stone_contract.totalAccruedPendingDelegations() == 0 )
    assert ( stone_contract.balanceOf( accounts[ 0 ] ) == 0 )
    assert ( stone_contract.balanceOf( accounts[ 1 ] ) == amount * 2 )
    assert (
        stone_contract.totalClaimableBalance() == amount * 4 * 3333 / 10000
    )

    # rand = random()
    # if (rand <= 0.5):
    #     stake_tx10 = stake(amount*2, stone_contract, lone_contract, one)
    #     expectedOutput10 = [amount*4*3333/10000, amount*4*3333/10000, amount*2*3334/10000]
    #     expectedPendingDelegation10 = [0, 0, amount*2*3334/10000]
    #     for index, validator in enumerate(validators):
    #         delegation_by_validator = staking.get_delegation_by_delegator_and_validator(
    #             stone_contract.address, validator, test_net)
    #         delegation_amount_by_validator = delegation_by_validator if delegation_by_validator != None else {}
    #         assert(delegation_amount_by_validator.get('amount', None) == expectedOutput10[index])
    #         assert(stone_contract.accruedPendingDelegations(convert_one_to_hex(validators[index])) == expectedPendingDelegation10[index])
    #     assert(stone_contract.balance() == amount*2*3334/10000)
    #     assert(stone_contract.totalAccruedPendingDelegations() == amount*2*3334/10000)
    #     assert(stone_contract.balanceOf(one) == amount*2)
    #     assert(stone_contract.balanceOf(two) == amount*2)
    #     assert(stone_contract.totalClaimableBalance() == 0)
    # else:
    countdown( 30 )  ##### Waiting for the next epoch
    stake_tx6 = stake(
        amount * 2,
        stone_contract,
        lone_contract,
        accounts[ 0 ]
    )
    expectedOutput6 = [
        amount * 2 * 3333 / 10000,
        amount * 2 * 3333 / 10000,
        amount * 2 * 3334 / 10000
    ]
    expectedPendingDelegation6 = [
        amount * 2 * 3333 / 10000,
        amount * 2 * 3333 / 10000,
        amount * 2 * 3334 / 10000
    ]
    for index, validator in enumerate( validators ):
        delegation_by_validator = staking.get_delegation_by_delegator_and_validator(
            stone_contract.address,
            validator,
            test_net
        )
        delegation_amount_by_validator = delegation_by_validator if delegation_by_validator != None else {}
        assert (
            delegation_amount_by_validator.get( 'amount',
                                                None ) ==
            expectedOutput6[ index ]
        )
        assert (
            stone_contract.accruedPendingDelegations(
                convert_one_to_hex( validators[ index ] )
            ) == expectedPendingDelegation6[ index ]
        )
    assert (
        stone_contract.balance() ==
        ( amount * 8 * 3333 / 10000 + amount * 2 * 3334 / 10000 )
    )
    assert (
        stone_contract.totalAccruedPendingDelegations() == amount * 4 * 3333 /
        10000 + amount * 2 * 3334 / 10000
    )
    assert ( stone_contract.balanceOf( accounts[ 0 ] ) == amount * 2 )
    assert ( stone_contract.balanceOf( accounts[ 1 ] ) == amount * 2 )
    assert (
        stone_contract.totalClaimableBalance() == amount * 4 * 3333 / 10000
    )

    countdown( 10 )
    stake_tx7 = stake(
        amount * 3,
        stone_contract,
        lone_contract,
        accounts[ 1 ]
    )
    expectedOutput7 = [
        amount * 7 * 3333 / 10000,
        amount * 7 * 3333 / 10000,
        amount * 7 * 3334 / 10000
    ]
    expectedPendingDelegation7 = [ 0, 0, 0 ]
    for index, validator in enumerate( validators ):
        delegation_by_validator = staking.get_delegation_by_delegator_and_validator(
            stone_contract.address,
            validator,
            test_net
        )
        delegation_amount_by_validator = delegation_by_validator if delegation_by_validator != None else {}
        assert (
            delegation_amount_by_validator.get( 'amount',
                                                None ) ==
            expectedOutput7[ index ]
        )
        assert (
            stone_contract.accruedPendingDelegations(
                convert_one_to_hex( validators[ index ] )
            ) == expectedPendingDelegation7[ index ]
        )
    assert ( stone_contract.balance() == ( amount * 4 ) )
    assert ( stone_contract.totalAccruedPendingDelegations() == 0 )
    assert ( stone_contract.balanceOf( accounts[ 0 ] ) == amount * 2 )
    assert ( stone_contract.balanceOf( accounts[ 1 ] ) == amount * 5 )
    assert ( stone_contract.totalClaimableBalance() == amount * 4 )

    countdown( 120 )
    index_id = lone_contract.tokenOfOwnerByIndex(
        accounts[ 1 ],
        lone_contract.balanceOf( accounts[ 1 ] ) - 1
    )
    stake_tx11 = claim( index_id, stone_contract, lone_contract, accounts[ 1 ] )
    expectedOutput11 = [
        amount * 5 * 3333 / 10000,
        amount * 5 * 3333 / 10000,
        amount * 6 * 3334 / 10000
    ]
    expectedPendingDelegation7 = [ 0, 0, 0 ]
    for index, validator in enumerate( validators ):
        delegation_by_validator = staking.get_delegation_by_delegator_and_validator(
            stone_contract.address,
            validator,
            test_net
        )
        delegation_amount_by_validator = delegation_by_validator if delegation_by_validator != None else {}
        assert (
            delegation_amount_by_validator.get( 'amount',
                                                None ) ==
            expectedOutput7[ index ]
        )
        assert (
            stone_contract.accruedPendingDelegations(
                convert_one_to_hex( validators[ index ] )
            ) == expectedPendingDelegation7[ index ]
        )
    assert ( stone_contract.balance() == ( amount ) )
    assert ( stone_contract.totalAccruedPendingDelegations() == 0 )
    assert ( stone_contract.balanceOf( accounts[ 0 ] ) == amount * 2 )
    assert ( stone_contract.balanceOf( accounts[ 1 ] ) == amount * 5 )
    assert ( stone_contract.totalClaimableBalance() == amount )
    # stake_tx6 = stake(amount*6, stone_contract, lone_contract, one)
    # expectedOutput7 = [amount*6*3333/10000, amount*6*3333/10000, amount*3*3334/10000+amount*3334/10000+ amount*6*3334/10000]
    # expectedPendingDelegation3 = [0, 0, 0]
    # for index, validator in enumerate(validators):
    #     delegation_by_validator = staking.get_delegation_by_delegator_and_validator(
    #         stone_contract.address, validator, test_net)
    #     delegation_amount_by_validator = delegation_by_validator if delegation_by_validator != None else {}
    #     assert(delegation_amount_by_validator.get('amount', None) == expectedOutput6[index])
    #     assert(stone_contract.accruedPendingDelegations(convert_one_to_hex(validators[index])) == expectedPendingDelegation6[index])
    # assert(stone_contract.balance() == (amount*4*3333/10000))
    # assert(stone_contract.totalAccruedPendingDelegations() == amount*4*3333/10000)
    # assert(stone_contract.balanceOf(one) == amount*8)
    # assert(stone_contract.balanceOf(two) == amount*2)

    # unstake_tx3 = unstake(amount, stone_contract, lone_contract, one)
    # unstake_tx4 = unstake(amount*1.5, stone_contract, lone_contract, three)
    # unstake_tx5 = unstake(amount, stone_contract, lone_contract, two)
    #
    # expectedOutput5 = [0, 0, amount*3*3334/10000+amount*(1+2)*3334/10000- amount*4*3334/10000- amount*3334/10000]
    # for index, validator in enumerate(validators):
    #     delegation_by_validator = staking.get_delegation_by_delegator_and_validator(
    #         stone_contract.address, validator, test_net)
    #     delegation_amount_by_validator = delegation_by_validator if delegation_by_validator != None else {}
    #     assert(delegation_amount_by_validator.get('amount', None) == expectedOutput5[index])
    #     assert(stone_contract.accruedPendingDelegations(convert_one_to_hex(validators[index])) == expectedPendingDelegation3[index])
    # assert(stone_contract.balance() == (amount*4*3333/10000))
    # assert(stone_contract.totalAccruedPendingDelegations() == amount*4*3333/10000)
    # assert(stone_contract.balanceOf(one) == 0)
    # assert(stone_contract.balanceOf(two) == amount)


def test_simple_unstake():
    print( "Initiating staking contract with one validator..." )
    print(
        "Creating the validator at {} using the Harmony SDK"
        .format( validator_address )
    )
    load_wallets()
    create_validator(
        validator_address,
        validator_info,
        accounts[ 0 ].private_key
    )
    stone_contract, lone_contract = deploy_from_address( accounts[ 0 ] )
    while stone_contract._epoch() < 2:
        countdown( 10 )
    input = amount * 10
    stake_tx = stake(
        input,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )

    unstake_tx = unstake(
        amount * 6,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )
    epoch = lone_contract.getMintedEpochOfTokenByIndex(
        lone_contract.balanceOf( accounts[ 0 ].address ) - 1
    )
    print( "Epoch..........", epoch )
    expected_SONE = 4 * amount
    expected_total_tokens = 1
    expected_balance_lone = 6 * amount
    delegation_by_delegator = staking.get_delegation_by_delegator_and_validator(
        stone_contract.address,
        validator_address,
        test_net
    )
    assert (
        stone_contract.balanceOf( accounts[ 0 ].address ) == expected_SONE
    )
    assert (
        lone_contract.balanceOf( accounts[ 0 ].address
                                ) == expected_total_tokens
    )
    token_id = lone_contract.tokenOfOwnerByIndex( accounts[ 0 ].address, 0 )
    assert (
        lone_contract.getAmountOfTokenByIndex( token_id ) ==
        expected_balance_lone
    )

    #################### 2nd Unstake ######################################
    unstake_tx2 = unstake(
        amount * 2,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )
    epoch_2 = lone_contract.getMintedEpochOfTokenByIndex(
        lone_contract.balanceOf( accounts[ 0 ].address ) - 1
    )
    print( "Epoch..........", epoch_2 )
    expected_SONE_2 = 2 * amount
    assert (
        stone_contract.balanceOf( accounts[ 0 ].address ) == expected_SONE_2
    )
    if ( epoch == epoch_2 ):
        expected_total_tokens_2 = expected_total_tokens
        expected_balance_lone_2 = 8 * amount
        delegation_by_delegator = staking.get_delegation_by_delegator_and_validator(
            stone_contract.address,
            validator_address,
            test_net
        )
        assert (
            lone_contract.balanceOf( accounts[ 0 ].address
                                    ) == expected_total_tokens_2
        )
        token_id_2 = lone_contract.tokenOfOwnerByIndex(
            accounts[ 0 ].address,
            expected_total_tokens_2 - 1
        )
        assert (
            lone_contract.getAmountOfTokenByIndex( token_id_2 ) ==
            expected_balance_lone_2
        )
    else:
        expected_total_tokens_2 = expected_total_tokens + 1
        expected_balance_lone_2 = 2 * amount
        delegation_by_delegator = staking.get_delegation_by_delegator_and_validator(
            stone_contract.address,
            validator_address,
            test_net
        )
        assert (
            lone_contract.balanceOf( accounts[ 0 ].address
                                    ) == expected_total_tokens_2
        )
        token_id_2 = lone_contract.tokenOfOwnerByIndex(
            accounts[ 0 ].address,
            expected_total_tokens_2 - 1
        )
        assert (
            lone_contract.getAmountOfTokenByIndex( token_id_2 ) ==
            expected_balance_lone_2
        )
    print( "Epoch..........", stone_contract._epoch() )
    ################################# 3rd Unstake ###################################
    countdown( 40 )  # ensuring the test enters a new epoch
    print( "Epoch..........", stone_contract._epoch() )
    print(
        "Account Balance:.............{}".format( stone_contract.balance() )
    )
    print(
        "User Stone Balance:.............{}".format(
            stone_contract.balanceOf( accounts[ 0 ].address )
        )
    )

    unstake_tx3 = unstake(
        amount,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )
    epoch_3 = lone_contract.getMintedEpochOfTokenByIndex(
        lone_contract.balanceOf( accounts[ 0 ].address ) - 1
    )
    print( "Epoch..........", epoch_3 )
    expected_SONE_3 = amount
    expected_total_tokens_3 = expected_total_tokens_2 + 1
    expected_balance_lone_3 = amount
    delegation_by_delegator = staking.get_delegation_by_delegator_and_validator(
        stone_contract.address,
        validator_address,
        test_net
    )
    assert (
        stone_contract.balanceOf( accounts[ 0 ].address ) == expected_SONE_3
    )
    assert (
        lone_contract.balanceOf( accounts[ 0 ].address
                                ) == expected_total_tokens_3
    )
    token_id_3 = lone_contract.tokenOfOwnerByIndex(
        accounts[ 0 ].address,
        expected_total_tokens_3 - 1
    )
    assert (
        lone_contract.getAmountOfTokenByIndex( token_id_3 ) ==
        expected_balance_lone_3
    )


def test_claim():
    print( "Initiating staking contract with one validator..." )
    print(
        "Creating the validator at {} using the Harmony SDK"
        .format( validator_address )
    )
    load_wallets()
    create_validator(
        validator_address,
        validator_info,
        accounts[ 0 ].private_key
    )

    stone_contract, lone_contract = deploy()
    while stone_contract._epoch() < 2:
        countdown( 10 )
    input_value = amount * 10
    stake_tx = stake(
        input_value,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )
    unstake_tx = unstake(
        amount * 6,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )
    epoch = lone_contract.getMintedEpochOfTokenByIndex(
        lone_contract.balanceOf( accounts[ 0 ].address ) - 1
    )
    print( "Epoch..........", epoch )
    countdown( 15 )
    unstake_tx2 = unstake(
        amount * 2,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )
    epoch_2 = lone_contract.getMintedEpochOfTokenByIndex(
        lone_contract.balanceOf( accounts[ 0 ].address ) - 1
    )
    print( "Epoch..........", epoch_2 )
    countdown( 200 )

    total_tokens = lone_contract.balanceOf( accounts[ 0 ].address )
    for index in range( total_tokens ):
        epoch, amount_to_pay = lone_contract.getMintedEpochOfTokenByIndex( index ), lone_contract.getAmountOfTokenByIndex( index )
        print(
            "Epoch difference....................",
            stone_contract._epoch() - epoch
        )
        initial_sone_balance = stone_contract.balance()
        print( "Initial Balance.....................", initial_sone_balance )
        claim1 = claim( index, stone_contract, lone_contract, accounts[ 0 ] )
        final_sone_balance = stone_contract.balance()
        print( "Final Balance.....................", final_sone_balance )
        assert ( initial_sone_balance - final_sone_balance == amount_to_pay )


def test_redelegation():
    print( "Initiating staking contract with one validator..." )
    print(
        "Creating the validator at {} using the Harmony SDK"
        .format( validator_address )
    )
    load_wallets()
    create_validator(
        validator_address,
        validator_info,
        accounts[ 0 ].private_key
    )
    create_spare_validators()
    stone_contract, lone_contract = deploy_with_3_validators()
    while stone_contract._epoch() < 2:
        countdown( 10 )
    input_value = amount * 10

    stake_tx = stake(
        input_value,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )
    print(
        "total {}".format( stone_contract.totalAccruedPendingDelegations() )
    )
    unstake_tx = unstake(
        amount * 4,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )
    print(
        "total {}".format( stone_contract.totalAccruedPendingDelegations() )
    )
    epoch = lone_contract.getMintedEpochOfTokenByIndex(
        lone_contract.balanceOf( accounts[ 0 ].address ) - 1
    )
    print( "Epoch..........", epoch )
    countdown( 20 )
    unstake_tx2 = unstake(
        amount * 2,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )
    print(
        "total {}".format( stone_contract.totalAccruedPendingDelegations() )
    )
    epoch_2 = lone_contract.getMintedEpochOfTokenByIndex(
        lone_contract.balanceOf( accounts[ 0 ].address ) - 1
    )
    print( "Epoch..........", epoch_2 )
    countdown( 20 )
    total_tokens = lone_contract.balanceOf( accounts[ 0 ].address )
    print( "len..........", total_tokens )
    for index in range( total_tokens ):
        print( "Redelegating tokenId", index )
        epoch, amount_to_pay = lone_contract.getMintedEpochOfTokenByIndex( index ), lone_contract.getAmountOfTokenByIndex( index )
        print( "Amount to pay {} at {} index".format( amount_to_pay, index ) )
        print(
            "Epoch difference....................",
            stone_contract._epoch() - epoch
        )
        totalStaked, supply = stone_contract.totalStaked(), stone_contract.totalSupply()
        initial_sone_balance = stone_contract.balanceOf( accounts[ 0 ].address )
        print( "Initial Balance.....................", initial_sone_balance )
        print(
            "Current Epoch........{} and minted epoch is {}".format(
                stone_contract._epoch(),
                epoch
            )
        )
        # if index==1:
        #     redelegation = redelegate1(index,stone_contract, lone_contract, accounts[0].address)

        redelegation = redelegate(
            index,
            stone_contract,
            lone_contract,
            accounts[ 0 ]
        )
        if ( amount_to_pay <= 300 ):
            assert (
                stone_contract.totalPendingReDelegation() == amount_to_pay
            )

        final_sone_balance = stone_contract.balanceOf( accounts[ 0 ].address )
        print( "Final Balance.....................", final_sone_balance )
        assert (
            supply * amount_to_pay / totalStaked == final_sone_balance -
            initial_sone_balance
        )

    while ( stone_contract._epoch() - epoch_2 < 7 ):
        countdown( 2 )

    # stake_tx = stake(
    #     amount,
    #     stone_contract,
    #     lone_contract,
    #     accounts[ 0 ].address
    # )

    # assert( stone_contract.totalAccruedPendingDelegations() == amount - 2*3333/10000 * amount )

    #####################handles the case where delegation epoch is not same as the current epoch##########

    # with pytest.raises(ValueError):
    #     unstake_tx = unstake(amount*5, stone_contract, lone_contract, accounts[0].address)
    #     redelegation = redelegate(2,stone_contract, lone_contract, accounts[0].address)


def test_redelegation_complex():
    load_wallets()
    create_validator(
        validator_address,
        validator_info,
        accounts[ 0 ].private_key
    )
    create_spare_validators()
    stone_contract, lone_contract = deploy()
    while stone_contract._epoch() < 2:
        countdown( 10 )
    input_value = amount * 10

    stake_tx = stake(
        input_value,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )
    unstake_tx = unstake(
        amount * 4,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )
    unstake_epoch = lone_contract.getMintedEpochOfTokenByIndex(
        lone_contract.balanceOf( accounts[ 0 ].address ) - 1
    )
    while ( unstake_epoch > stone_contract._epoch() - 5 ):
        countdown( 2 )
    stake_tx = stake(
        input_value,
        stone_contract,
        lone_contract,
        accounts[ 1 ].address
    )
    unstake_tx = unstake(
        amount * 4,
        stone_contract,
        lone_contract,
        accounts[ 1 ].address
    )
    index = 1
    while ( unstake_epoch > stone_contract._epoch() - 8 ):
        countdown( 2 )
    redelegation = redelegate(
        index,
        stone_contract,
        lone_contract,
        accounts[ 1 ]
    )
    assert ( stone_contract.totalClaimableBalance() == amount * 4 )


def test_claim_multiple_users():
    load_wallets()
    create_validator(
        validator_address,
        validator_info,
        accounts[ 0 ].private_key
    )
    create_spare_validators()
    stone_contract, lone_contract = deploy_with_3_validators()
    while stone_contract._epoch() < 2:
        countdown( 10 )
    input_value = amount * 10
    stake_tx = stake(
        input_value,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )
    unstake_tx = unstake(
        amount * 4,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )
    stake_tx = stake(
        input_value,
        stone_contract,
        lone_contract,
        accounts[ 1 ].address
    )
    unstake_tx = unstake(
        amount * 5,
        stone_contract,
        lone_contract,
        accounts[ 1 ].address
    )
    stake_tx = stake(
        input_value,
        stone_contract,
        lone_contract,
        accounts[ 2 ]
    )
    unstake_tx = unstake(
        amount * 6,
        stone_contract,
        lone_contract,
        accounts[ 2 ]
    )
    unstake_epoch = lone_contract.getMintedEpochOfTokenByIndex(
        lone_contract.balanceOf( accounts[ 0 ].address ) - 1
    )
    while ( unstake_epoch > stone_contract._epoch() - 9 ):
        countdown( 2 )
    assert ( stone_contract.balance() == amount * 15 )
    redelegation = claim(
        0,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )
    assert ( stone_contract.totalClaimableBalance() == amount * 11 )
    redelegation = claim(
        1,
        stone_contract,
        lone_contract,
        accounts[ 1 ].address
    )
    assert ( stone_contract.totalClaimableBalance() == amount * 6 )
    redelegation = claim( 2, stone_contract, lone_contract, accounts[ 2 ] )
    assert ( stone_contract.totalClaimableBalance() == amount * 0 )


def test_redelegation_after_7_epoch():
    load_wallets()
    create_validator(
        validator_address,
        validator_info,
        accounts[ 0 ].private_key
    )
    create_spare_validators()
    stone_contract, lone_contract = deploy()
    while stone_contract._epoch() < 2:
        countdown( 10 )
    input_value = amount * 10

    stake_tx = stake(
        input_value,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )
    unstake_tx = unstake(
        amount * 2,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )
    unstake_epoch = lone_contract.getMintedEpochOfTokenByIndex(
        lone_contract.balanceOf( accounts[ 0 ].address ) - 1
    )
    while ( unstake_epoch > stone_contract._epoch() - 8 ):
        countdown( 2 )
    index = 0
    redelegation = redelegate(
        index,
        stone_contract,
        lone_contract,
        accounts[ 0 ].address
    )
    assert ( stone_contract.totalPendingReDelegation() == 0.0 )
    assert ( stone_contract.totalClaimableBalance() == 0.0 )
    assert ( stone_contract.balance() == 0.0 )
