from brownie import accounts, stONE, oneLidoNFT, Contract, StakingContract, config
from pyhmy import account, transaction, staking, signing, blockchain, numbers, staking_structures, staking_signing
from pyhmy.validator import Validator
from pyhmy.util import convert_one_to_hex
from utils.constants import *
import sys
from time import sleep

test_net = config[ "node" ][ "test_net" ]


def fund_address( how_much, address, **kwargs ):
    load_wallets()
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = test_net
    )
    transaction_dict = {
        'nonce': nonce,
        'gasPrice': int( 1e9 ),
        'gas': kwargs.get( 'gas',
                           21000 ),
        'to': address,
        'value': int( numbers.convert_one_to_atto( how_much ) ),
        'chainId': 2,
        'shardID': 0,
        'toShardID': kwargs.get( 'toShardID',
                                 0 ),
    }
    signed_tx = signing.sign_transaction(
        transaction_dict,
        private_key = accounts[ 0 ].private_key
    )
    return transaction.send_and_confirm_raw_transaction(
        signed_tx.rawTransaction.hex(),
        endpoint = test_net
    )


def load_wallets():
    accounts.add( config[ "wallets" ][ "from_key_1" ] )
    accounts.add( config[ "wallets" ][ "from_key_2" ] )
    accounts.add( config[ "wallets" ][ "from_key_3" ] )


def countdown( t ):
    for i in range( t, 0, -1 ):
        print( f"{i}", end = "\r", flush = True )
        sleep( 1 )


def create_validator( address, info, private_key ):
    # address must be a bech32 (one...) address
    validators = staking.get_all_validator_addresses( endpoint = test_net )
    if address in validators:
        return
    original_count = len( validators )
    validator = Validator( address )
    validator.load( info )
    nonce = account.get_account_nonce( address, 'latest', endpoint = test_net )
    # nonce, gas_price, gas_limit, private_key, chain_id
    signed_tx = validator.sign_create_validator_transaction(
        nonce,
        int( 1e9 ),
        55000000,
        private_key,
        2
    )
    hash = transaction.send_raw_staking_transaction(
        signed_tx.rawTransaction.hex(),
        endpoint = test_net
    )
    # wait for tx to get processed
    while ( True ):
        tx = transaction.get_staking_transaction_by_hash(
            hash,
            endpoint = test_net
        )
        if tx is not None:
            if tx[
                'blockHash'
            ] != '0x0000000000000000000000000000000000000000000000000000000000000000':
                break
    # ensure it is created
    validators = staking.get_all_validator_addresses( endpoint = test_net )
    assert ( len( validators ) > original_count )
    # ensure it has correct info
    loaded_info = staking.get_validator_information(
        address,
        endpoint = test_net
    )
    assert ( loaded_info[ 'validator' ][ 'name' ] == info[ 'name' ] )
    assert ( loaded_info[ 'validator' ][ 'identity' ] == info[ 'identity' ] )


def fund_contract( how_much, contract ):
    nonce = account.get_account_nonce(
        validator_address,
        'latest',
        endpoint = test_net
    )
    money_tx = contract.acceptMoney(
        {
            'value': int( numbers.convert_one_to_atto( how_much ) ),
            'from': accounts[ 0 ].address,
            'nonce': nonce,
            'gas_limit': once_gas_limit
        }
    )
    w3.eth.wait_for_transaction_receipt( money_tx.txid )


def stake_rewards( stone_address, lone_contract ):
    stone_contract = Contract.from_abi( "stONE", stone_address, stONE.abi )
    tx = stone_contract.stakeRewards(
        {
            'from': accounts[ 0 ],
            'gas_limit': 500000
        }
    )
    print( "Total Supply: ", stone_contract.totalSupply() )
    print( "Total Staked: ", stone_contract.totalStaked() )


def deploy_with_3_validators():
    stONE.deploy(
        [
            convert_one_to_hex( validator_address ),
            convert_one_to_hex( spare_validators[ 0 ] ),
            convert_one_to_hex( spare_validators[ 1 ] )
        ],
        [ 3333,
          3333,
          3334 ],
        accounts[ 0 ].address,
        accounts[ 0 ].address,
        {
            'from': accounts[ 0 ],
            'gas_limit': w3.toWei( Decimal( '0.025' ),
                                   'gwei' ),
            'gas_price': w3.toWei( Decimal( '100' ),
                                   'gwei' )
        }
    )
    stone_contract = stONE[ -1 ]

    # stone_contract.stakeTest({'from': accounts[0], 'value': amount, 'gas_limit': w3.toWei(Decimal('0.0025'), 'gwei')})
    print( "stONE contract is at {}".format( stone_contract.address ) )
    none_address = stone_contract.nONE()
    print( "lONE contract is at {}".format( none_address ) )
    none_contract = Contract.from_abi( "nONE", none_address, oneLidoNFT.abi )
    return stone_contract, none_contract


def stake( amount1, stone_contract, lone_contract, address ):
    print( "Staking..." )
    stake_tx = stone_contract.stake(
        amount1,
        {
            'from': address,
            'value': amount1,
            'gas_limit': w3.toWei( Decimal( '0.0025' ),
                                   'gwei' ),
            'gas_price': w3.toWei( Decimal( '30' ),
                                   'gwei' )
        }
    )
    print( "Total Supply: ", stone_contract.totalSupply() )
    print( "Total Staked: ", stone_contract.totalStaked() )
    return stake_tx


def unstake( amount, stone_contract, lone_contract, address ):
    print( "Unstaking..." )
    unstake_tx = stone_contract.unstake(
        amount,
        {
            'from': address,
            'gas_limit': w3.toWei( Decimal( '0.0025' ),
                                   'gwei' ),
            'gas_price': w3.toWei( Decimal( '100' ),
                                   'gwei' )
        }
    )
    print( "stONE balance: ", stone_contract.balanceOf( address ) / 1e18 )
    return unstake_tx


def redelegate( tokenId, stone_contract, lone_contract, account ):
    print( "Redelegating..." )
    redelegate_tx = stone_contract.reDelegate(
        tokenId,
        {
            'from': account,
            'gas_limit': w3.toWei( Decimal( '0.0025' ),
                                   'gwei' ),
            'gas_price': w3.toWei( Decimal( '100' ),
                                   'gwei' )
        }
    )
    # print("stONE balance: ", stone_contract.balanceOf(account.address, {'from': accounts[0]} )/1e18)
    return redelegate_tx


def claim( tokenId, stone_contract, lone_contract, account ):
    print( "Claiming..." )
    claim_tx = stone_contract.claim(
        tokenId,
        {
            'from': account,
            'gas_limit': w3.toWei( Decimal( '0.0025' ),
                                   'gwei' )
        }
    )
    # print("lONE Balance: ", lone_contract.userBalance(accounts[0].address )/1e18)
    # print("Contract balance: ", stone_contract.balance() )
    return claim_tx


def set_admin_values( stone_contract, lone_contract ):
    print( "Setting Fee..." )
    stone_contract.setFee( 10 )

    print( "Setting FeeCollector..." )
    stone_contract.setFeeCollector( accounts[ 0 ].address )

    print( "Setting Rebalancer..." )
    stone_contract.setRebalancer( accounts[ 0 ].address )


def loop_stake( stone_contract, lone_contract ):
    while True:
        stake_rewards( stone_contract, lone_contract )
        print(
            "rewardsToDelegate: ",
            w3.fromWei( stone_contract.rewardsToDelegate(),
                        'ether' )
        )
        countdown( 60 )


def create_spare_validators():
    for addr, info, pk in zip( spare_validators, spare_validator_infos, spare_validator_pks ):
        if addr not in staking.get_all_validator_addresses(
            endpoint = test_net
        ):
            print( "Funding spare validator", addr )
            fund_address( 100000, convert_one_to_hex( addr ) )
            create_validator( addr, info, pk )


def rebalance_initiate( stone_contract ):
    stone_contract.rebalanceInitiate(
        [
            convert_one_to_hex( spare_validators[ 0 ] ),
            convert_one_to_hex( spare_validators[ 1 ] )
        ],
        [ 2000,
          3000 ],
        [ convert_one_to_hex( validator_address ) ],
        [ 5000 ],
        {
            'from': accounts[ 0 ],
            'gas_limit': 1000000
        }
    )
    print( "Rebalance initiated. Sleeping for 30 seconds" )
    countdown( 60 )


def rebalance_complete( stone_contract ):
    stone_contract.rebalanceComplete(
        {
            'from': accounts[ 0 ],
            'gas_limit': 1000000
        }
    )
    print( "Rebalance Completed" )


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


def fetch_epoch( drone_contract ):
    return drone_contract._epoch()


def deploy():
    stONE.deploy(
        [ convert_one_to_hex( validator_address ) ],
        [ 10000 ],
        accounts[ 0 ].address,
        accounts[ 0 ].address,
        {
            'from': accounts[ 0 ],
            'gas_limit': w3.toWei( Decimal( '0.025' ),
                                   'gwei' ),
            'gas_price': w3.toWei( Decimal( '25' ),
                                   'gwei' )
        }
    )
    stone_contract = stONE[ -1 ]

    # stone_contract.stakeTest({'from': accounts[0], 'value': amount, 'gas_limit': w3.toWei(Decimal('0.0025'), 'gwei')})
    print( "stONE contract is at {}".format( stone_contract.address ) )
    none_address = stone_contract.nONE()
    print( "lONE contract is at {}".format( none_address ) )
    none_contract = Contract.from_abi( "nONE", none_address, oneLidoNFT.abi )
    return stone_contract, none_contract


def deploy_from_address( from_address ):
    stONE.deploy(
        [ convert_one_to_hex( validator_address ) ],
        [ 10000 ],
        from_address.address,
        accounts[ 0 ].address,
        {
            'from': from_address,
            'gas_limit': w3.toWei( Decimal( '0.025' ),
                                   'gwei' ),
            'gas_price': w3.toWei( Decimal( '25' ),
                                   'gwei' )
        }
    )
    stone_contract = stONE[ -1 ]

    # stone_contract.stakeTest({'from': accounts[0], 'value': amount, 'gas_limit': w3.toWei(Decimal('0.0025'), 'gwei')})
    print( "stONE contract is at {}".format( stone_contract.address ) )
    none_address = stone_contract.nONE()
    print( "lONE contract is at {}".format( none_address ) )
    none_contract = Contract.from_abi( "nONE", none_address, oneLidoNFT.abi )
    return stone_contract, none_contract
