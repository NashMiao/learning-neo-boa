from boa.interop.Neo.Action import RegisterAction
from boa.interop.System.ExecutionEngine import *
from boa.interop.Ontology.Native import *
from boa.interop.Neo.Blockchain import *
from boa.interop.Neo.Storage import *
from boa.interop.Neo.Runtime import *
from boa.interop.Neo.Block import *
from boa.builtins import *

ctx = GetContext()
contract_address = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01')

OnTransfer = RegisterAction('transfer', 'address_from', 'address_to', 'amount')


def create_template(rule):
    """
    :param rule: list
    :return: bool
    """
    try:
        str_value = ''
        for q in range(0, len(rule)):
            str_value = str_value + str(rule[q])
        template_id = sha256(str_value)
        Put(ctx, template_id, rule)
        Log(template_id)
        Put(ctx, concat(template_id, 'count'), 0)
        return True
    except Exception:
        return False


def create_instance(template_id, metadata, payments, payer_threshold, payees, reviewer):
    """
    :param template_id: int
    :param metadata: str
    :param payments: tuple
    :param payer_threshold: int
    :param payees: list
    :param reviewer: str
    :return: bool
    """
    try:
        current_height = GetHeight()
        current_block = GetBlock(current_height)
        current_block_timestamp = current_block.Timestamp
        count = Get(ctx, concat(template_id, 'count'))
        data = concat(template_id, current_block_timestamp)
        data = concat(data, str(count))
        instance_id = sha256(data)
        Put(ctx, concat(instance_id, 'metadata'), metadata)
        Put(ctx, concat(instance_id, 'payments'), payments)
        Put(ctx, concat(instance_id, 'threshold'), payer_threshold)
        Put(ctx, concat(instance_id, 'payees'), payees)
        Put(ctx, concat(instance_id, 'reviewer'), reviewer)
        Put(ctx, concat(instance_id, 'balance'), 0)
        Put(ctx, concat(instance_id, 'lock'), False)
        Notify(['create', instance_id])
        count += 1
        Put(ctx, template_id, count)
        return True
    except Exception:
        return False


def input_asset(instance_id, amount, payer):
    """

    :param instance_id: str
    :param amount: int
    :param payer: str
    """
    script_hash = GetExecutingScriptHash()
    is_lock = Get(ctx, concat(instance_id, 'lock'))
    if is_lock:
        return False
    else:
        OnTransfer(payer, script_hash, amount)
        balance = Get(ctx, concat(instance_id, 'balance'))
        balance += amount
        Put(ctx, concat(instance_id, 'balance'), balance)
        Notify(['input', instance_id, amount, payer])


def lock(instance_id, lock_time, payers):
    """

    :param instance_id: str
    :param lock_time: str
    :param payers: list
    """
    is_lock = Get(ctx, concat(instance_id, 'lock'))
    if is_lock:
        return False
    else:
        Put(ctx, concat(instance_id, 'lock'), True)
        Put(ctx, concat(instance_id, 'lockTime'), lock_time)
        Put(ctx, concat(instance_id, 'payers'), payers)
        Notify(['Lock', instance_id])
        return True


def confirm(instance_id, confirmer):
    """

    :param instance_id: str
    :param confirmer: list
    """
    current_height = GetHeight()
    current_block = GetBlock(current_height)
    current_block_timestamp = current_block.Timestamp
    lock_time = Get(ctx, concat(instance_id, 'lockTime'))
    if current_block_timestamp < lock_time:
        return False
    else:
        from_acct = GetExecutingScriptHash()
        payees = Get(ctx, concat(instance_id, 'payees'))
        balance = Get(ctx, concat(instance_id, 'balance'))
        quota = Get(ctx, concat(instance_id, 'reviewerQuota'))
        if len(quota) == 0:
            quota = Get(ctx, instance_id)
        for index in range(0, len(payees)):
            amount = balance * quota[index]
            param = state(from_acct, payees[index], amount)
            Invoke(amount, contract_address, 'transfer', [param])
        Put(ctx, concat(instance_id, 'lock'), False)
        Notify(["Confirm", instance_id, confirmer])
        return True


def set_quota(instance_id, quota, reviewer):
    """

    :param instance_id: str
    :param quota: list
    :param reviewer: str
    :return:
    """
    if CheckWitness(reviewer):
        payees = Get(ctx, concat(instance_id, 'payees'))
        if len(payees) > len(quota):
            return False
        else:
            Put(ctx, concat(instance_id, 'reviewerQuota'), quota)
            Notify(['Quota', instance_id, quota])
            return True
    else:
        return False


def refund(instance_id, operator):
    """

    :param instance_id: str
    :param operator: str
    """
    if CheckWitness(operator):
        Notify(['Refund', instance_id, operator])
        return True
    else:
        return False


def main(operation, args):
    """
    This is the main entry point for the Smart Contract

    :param operation: the operation to be performed
    :param args: a list of arguments ( which may be empty, but not absent )
    :return: indicating the successful execution of the smart contract
    """
    if operation == 'create_template':
        create_template(args[0])
        return True
    elif operation == 'create_instance':
        if len(args) == 4:
            return create_instance(args[0], args[1], args[2], args[3], args[4], '')
        elif len(args) == 5:
            return create_instance(args[0], args[1], args[2], args[3], args[4], args[5])
        else:
            return False
    elif operation == 'input_asset':
        if len(args) == 3:
            payer = GetCallingScriptHash()
            if payer != args[2]:
                return False
            return input_asset(args[0], args[1], args[2])
        else:
            return False
    elif operation == 'lock':
        if len(args) == 3:
            return
    elif operation == 'confirm':
        if len(args) == 2:
            return confirm(args[0], args[1])
        else:
            return False
    elif operation == 'set_quota':
        if len(args) == 3:
            return set_quota(args[0], args[1], args[2])
        else:
            return False
    elif operation == 'refund':
        if len(args) == 2:
            return refund(args[0], args[1])
        else:
            return False
    else:
        return False


if __name__ == '__main__':
    while True:
        operation = input('operation: ')
        args = input('args: ')
        main(operation, args)
