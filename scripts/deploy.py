from brownie import accounts, stONE, oneLidoNFT, StakingContract
from pyhmy import staking, blockchain
from pyhmy.util import convert_one_to_hex
from utils.constants import *


def wait_for_rewards( stone_contract ):
    t = 0
    while int(
        staking.get_delegation_by_delegator_and_validator(
            stone_contract.address,
            validator_address,
            endpoint = 'http://192.168.3.215:9500'
        )[ 'reward' ]
    ) == 0:
        sleep( 10 )
        t += 10
        print( t )
        validator_information = staking.get_validator_information(
            validator_address,
            endpoint = test_net
        )
        print( validator_information[ 'active-status' ] )
        for delegation in validator_information[ 'validator' ][ 'delegations' ]:
            print(
                delegation[ 'delegator-address' ],
                "=>",
                delegation[ 'reward' ]
            )
        print( '-' * 50 )


def main():
    if blockchain.get_shard( test_net ) != 0:
        sys.exit( "Wrong network for shard 0" )
    print( "Setting up test environment" )

    accounts.add( pk )
    accounts.add( pk2 )
    accounts.add( pk1 )
    print( one, two, three )

    print( "Initiating staking contract with one validator..." )
    print(
        "Creating the validator at {} using the Harmony SDK"
        .format( validator_address )
    )
    create_validator( validator_address, validator_info, pk )
    create_spare_validators()
    stone_contract, lone_contract = deploy_with_3_validators()
    while stone_contract._epoch() < 2:
        countdown( 10 )
    input_value = amount * 10

    stake_tx = stake(
        input_value,
        stone_contract,
        lone_contract,
        accounts[ 0 ]
    )
    print(
        "total {}".format( stone_contract.totalAccruedPendingDelegations() )
    )
    unstake_tx = unstake(
        amount * 4,
        stone_contract,
        lone_contract,
        accounts[ 0 ]
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
        accounts[ 0 ]
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
        print(
            staking.get_delegation_by_delegator_and_validator(
                stone_contract.address,
                validator_address,
                test_net
            )
        )
        print(
            staking.get_delegation_by_delegator_and_validator(
                stone_contract.address,
                spare_validators[ 0 ],
                test_net
            )
        )
        print(
            staking.get_delegation_by_delegator_and_validator(
                stone_contract.address,
                spare_validators[ 1 ],
                test_net
            )
        )
        print( stone_contract.balance() )
        print(
            "validatorAddress.................",
            stone_contract.validatorPercentages(
                convert_one_to_hex( validator_address )
            ) * amount_to_pay / 10000
        )
        print(
            "spare_validator1",
            stone_contract.validatorPercentages(
                convert_one_to_hex( spare_validators[ 0 ] )
            ) * amount_to_pay / 10000
        )
        print(
            "spare_validator2",
            stone_contract.validatorPercentages(
                convert_one_to_hex( spare_validators[ 0 ] )
            ) * amount_to_pay / 10000
        )
        print(
            "total {}".format(
                stone_contract.totalAccruedPendingDelegations()
            )
        )
        redelegation = redelegate(
            index,
            stone_contract,
            lone_contract,
            accounts[ 0 ]
        )
        print(
            "total {}".format(
                stone_contract.totalAccruedPendingDelegations()
            )
        )
        final_sone_balance = stone_contract.balanceOf( accounts[ 0 ].address )
        print( "Final Balance.....................", final_sone_balance )

    # create_validator(validator_address, validator_info, pk)
    # create_spare_validators()
    # drone_contract, none_contract = deploy()
    #
    # while (fetch_epoch(drone_contract) < 2):
    #     countdown(1)
    #
    # epoch = fetch_epoch(drone_contract)
    # stake_tx = stake(amount*6, drone_contract, none_contract, accounts[2])
    #
    # while (epoch >= fetch_epoch(drone_contract)):
    #     countdown(5)
    # drone_contract.rebalanceInitiate([convert_one_to_hex(spare_validators[1]), convert_one_to_hex(validator_address), convert_one_to_hex(spare_validators[0])], [3333, 3334, 3333], {'from': accounts[0], 'gas_limit': w3.toWei(Decimal('0.025'), 'gwei'), 'gas_price': w3.toWei(Decimal('100'), 'gwei')})
    #
    # epoch = fetch_epoch(drone_contract)
    # while (epoch == fetch_epoch(drone_contract)-1):
    #     pass
    # unstake(amount*6, drone_contract, none_contract, accounts[2])
    # print ("isRebalancing...................", drone_contract.isRebalancing())
    # print ("Supply...................", drone_contract.totalSupply())
    # print ("ExchnageRate...................", drone_contract.totalSupply() / drone_contract.totalStaked())
    # print ("_initialClaimableBalance...................", drone_contract.totalClaimableBalance())
    #
    # stake(amount*10, drone_contract, none_contract, accounts[0])
    # print ("_InitiateRebalance...................", drone_contract.rebalanceInitiateEpoch())
    # print ("_RebalanceComplete...................", drone_contract.rebalanceCompleteEpoch())
    # print ("_CurrentEpoch...................", drone_contract._epoch())
    # epoch = fetch_epoch(drone_contract)
    # print ("TotalAccrued...................", drone_contract.totalAccruedPendingDelegations() )
    # print ("TotalAccountBalance.............", drone_contract.balance())
    #
    # print(staking.get_delegation_by_delegator_and_validator(drone_contract.address, validator_address, test_net ))
    # print(staking.get_delegation_by_delegator_and_validator(drone_contract.address, spare_validators[0], test_net ))
    # print(staking.get_delegation_by_delegator_and_validator(drone_contract.address, spare_validators[1], test_net ))
    # #
    # epoch = fetch_epoch(drone_contract)
    # while (fetch_epoch(drone_contract) -2 <= epoch):
    #     countdown(10)
    # print("CurrentEpoch...............", fetch_epoch(drone_contract))
    #
    #
    # drone_contract.rebalanceComplete({'from': accounts[0], 'gas_limit': w3.toWei(Decimal('0.025'), 'gwei'), 'gas_price': w3.toWei(Decimal('25'), 'gwei')})
    # print(staking.get_delegation_by_delegator_and_validator(drone_contract.address, validator_address, test_net ))
    # print(staking.get_delegation_by_delegator_and_validator(drone_contract.address, spare_validators[0], test_net ))
    # print(staking.get_delegation_by_delegator_and_validator(drone_contract.address, spare_validators[1], test_net ))
    #
    # print("Current Account Balance................", drone_contract.balance())
    # unstake(amount*6, drone_contract, none_contract, accounts[0])
    # print(staking.get_delegation_by_delegator_and_validator(drone_contract.address, validator_address, test_net ))
    # print(staking.get_delegation_by_delegator_and_validator(drone_contract.address, spare_validators[0], test_net ))
    # print(staking.get_delegation_by_delegator_and_validator(drone_contract.address, spare_validators[1], test_net ))
    # print("Current Account Balance................", drone_contract.balance())
    # for index, addr in enumerate([validator_address]+spare_validators):
    #     print ("TotalStaked in {} is {}".format(addr, drone_contract.validatorStakedAmount(convert_one_to_hex(addr))))
    # countdown(120)
    # print("Current Account Balance................", drone_contract.balance())
