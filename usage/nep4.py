from boa.interop.Neo.Storage import *
from boa.interop.Neo.Runtime import *
from boa.builtins import concat

ctx = GetContext()

NAME = 'DXToken'
SYMBOL = 'DX'
DECIMAL = 8
FACTOR = 100000000
OWNER = bytearray(b'\xe9\x8f\x49\x98\xd8\x37\xfc\xdd\x44\xa5\x05\x61\xf7\xf3\x21\x40\xc7\xc6\xc2\x60')
TOTAL_AMOUNT = 1000000000
TRANSFER_PREFIX = bytearray(b'\x01')
APPROVE_PREFIX = bytearray(b'\x02 ')

SUPPLY_KEY = 'totoalSupply'


def Main(operation, args):
    """
    :param operation:
    :param args:
    :return:
    """
    if operation == 'Name':
        return Name()
    if operation == 'TotalSupply':
        return TotalSupply()
    if operation == 'Init':
        return Init()
    if operation == 'Symbol':
        return Symbol()
    if operation == 'Decimal':
        return Decimal()
    if operation == 'Transfer':
        if len(args) != 3:
            return False
        else:
            from_acct = args[0]
            to_acct = args[1]
            amount = args[2]
            return Transfer(from_acct, to_acct, amount)
    if operation == 'TransferMuti':
        return TransferMulti(args)
    if operation == 'Approve':
        if len(args) != 3:
            return False
        owner = args[0]
        spender = args[1]
        amount = args[2]
        return Approve(owner, spender, amount)
    if operation == 'TransferFrom':
        if len(args) != 4:
            return False
        spender = args[0]
        from_acct = args[1]
        to_acct = args[2]
        amount = args[3]
        return TransferFrom(spender, from_acct, to_acct, amount)
    if operation == 'BalanceOf':
        if len(args) != 1:
            return False
        acct = args[0]
        return BalanceOf(acct)
    if operation == 'Allowance':
        if len(args) != 2:
            return 0
        owner = args[0]
        spender = args[1]
        return Allowance(owner, spender)


def Name():
    return NAME


def TotalSupply():
    return TOTAL_AMOUNT * FACTOR


def Init():
    if Get(ctx, SUPPLY_KEY):
        Notify('Already initialized!')
        return False
    else:
        total = TOTAL_AMOUNT * FACTOR
        Put(ctx, SUPPLY_KEY, total)
        Put(ctx, concat(TRANSFER_PREFIX, OWNER), total)
        Notify(['transfer', '', OWNER, total])
        return True


def Symbol():
    return SYMBOL


def Transfer(from_acct, to_acct, amount):
    if from_acct == to_acct:
        return True
    if amount == 0:
        return True
    if amount < 0:
        return False
    if CheckWitness(from_acct) == False:
        return False
    if len(to_acct) != 20:
        return False
    fromKey = concat(TRANSFER_PREFIX, from_acct)
    fromBalance = Get(ctx, fromKey)
    if fromBalance < amount:
        return False
    if fromBalance == amount:
        Delete(ctx, fromKey)
    else:
        Put(ctx, fromKey, fromBalance - amount)

    tokey = concat(TRANSFER_PREFIX, to_acct)
    toBalance = Get(ctx, tokey)

    Put(ctx, tokey, toBalance + amount)
    Notify(['transfer', from_acct, to_acct, amount])
    return True


def TransferMulti(args):
    for p in args:
        if len(p) != 3:
            return False
        if Transfer(p[0], p[1], p[2]):
            return True
        else:
            return False


def Approve(owner, spender, amount):
    if amount < 0:
        return False
    if CheckWitness(owner) == False:
        return False
    key = concat(concat(APPROVE_PREFIX, owner), spender)
    allowance = Get(ctx, key)
    Put(ctx, key, amount + allowance)
    Notify(['approve', owner, spender, amount])
    return True


def TransferFrom(spender, from_acct, to_acct, amount):
    if amount < 0:
        return False
    if CheckWitness(spender) == False:
        return False
    appoveKey = concat(concat(APPROVE_PREFIX, from_acct), spender)
    approvedAmount = Get(ctx, appoveKey)
    if approvedAmount < amount:
        return False
    if approvedAmount == amount:
        Delete(ctx, appoveKey)
    else:
        Put(ctx, appoveKey, approvedAmount - amount)

    if len(to_acct) != 20:
        return False
    fromKey = concat(TRANSFER_PREFIX, from_acct)
    fromBalance = Get(ctx, fromKey)
    if fromBalance < amount:
        return False
    if fromBalance == amount:
        Delete(ctx, fromKey)
    else:
        Put(ctx, fromKey, fromBalance - amount)

    tokey = concat(TRANSFER_PREFIX, to_acct)
    toBalance = Get(ctx, tokey)

    Put(ctx, tokey, toBalance + amount)
    Notify(['transfer', from_acct, to_acct, amount])
    return True


def BalanceOf(account):
    return Get(ctx, concat(TRANSFER_PREFIX, account))


def Decimal():
    return DECIMAL


def Allowance(owner, spender):
    allowanceKey = concat(concat(APPROVE_PREFIX, owner), spender)
    return Get(ctx, allowanceKey)


if __name__ == '__main__':
    while True:
        operation = input('operation: ')
        args = input('args: ')
        ret = Main(operation, args)
        if isinstance(ret, bool):
            if ret:
                print('True')
            else:
                print('False')
        else:
            print(ret)
