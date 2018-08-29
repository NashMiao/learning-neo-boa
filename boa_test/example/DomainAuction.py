"""
An Example on domain auction
"""
from boa.interop.System.Storage import *
from boa.interop.System.Runtime import *
from boa.interop.System.ExecutionEngine import *
from boa.builtins import concat
from boa.interop.Ontology.Native import *
ctx = GetContext()
selfAddr = GetExecutingScriptHash()

#ONT native contract address
contractAddress = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01')


def Main(operation, args):

    if operation == 'register':
        acct = args[0]
        url = args[1]
        if CheckWitness(acct):
            return register(acct,url)
        Notify('CheckWitness failed!')
        return False
    
    if operation == 'sell':
        acct = args[0]
        url = args[1]
        price = args[2]
        if CheckWitness(acct):
            return sell(acct,url,price)
        Notify('CheckWitness failed!')
        return False

    if operation == 'query':
        url = args[0]
        return query(url)

    if operation == 'buy':
        acct = args[0]
        url = args[1]
        price = args[2]
        if CheckWitness(acct):
            return buy(acct,url,price)
        Notify('CheckWitness failed!')
        return False

    if operation == 'done':
        acct = args[0]
        url = args[1]
        if CheckWitness(acct):
            return done(acct,url)
        Notify('CheckWitness failed!')
        return False

    if operation == 'transfer':
        fromacct = args[0]
        amount = args[1]
        return transferONT(fromacct,selfAddr,amount)

    Notify('Not a supported operation!')
    return True


def register(account,domain):
    """
    register an domain for account
    :param account:
    :param domain:
    :return:
    """
    if not Get(ctx,domain):
        Put(ctx,domain,account)
        Notify('register succeed!')
        return True
    Notify('already registered!')
    return False


def sell(account,url, price):
    """
    sell the domain at a price
    :param account:
    :param url:
    :param price:
    :return:
    """
    owner = Get(ctx,url)
    if owner == account :
        Put(ctx,concat('Original_Owner_',url),account)
        Put(ctx,concat('Price_',url),price)
        Put(ctx,url,selfAddr)
        Notify('sell succeed!')
        return True
    Notify('Not a owner')
    return False


def query(url):
    """
    query a domain owner
    :param url:
    :return:
    """
    owner = Get(ctx,url)
    Notify(concat('owner is ',owner))
    return owner


def buy(acct,url,price):
    """
    buy a domain a price
    :param acct:
    :param url:
    :param price:
    :return:
    """
    owner = Get(ctx,url)
    if owner != selfAddr:
        Notify("url not in sale!")
        return False

    prevBuyer = Get(ctx,concat('TP_',url))
    currentPrice = Get(ctx,concat('Price_',url))
    #no buyer before case
    if not prevBuyer:
        if price >= currentPrice:
            if transferONT(acct, selfAddr, price):
                Put(ctx,concat('TP_',url),acct)
                if price > currentPrice:
                    Put(ctx,concat('Price_',url),price)
                Notify('buy succeed!')
                return True
            else:
                Notify('Transfer Failed')
                return False
        Notify('Price is lower than current price')
        return False
    # has buyer before case
    if price <= currentPrice:
        Notify('Price is lower than current price')
        return False
    if transferONT(selfAddr,acct,currentPrice):
        Put(ctx,concat('TP_',url),acct)
        Put(ctx,concat('Price_',url),price)
        Notify('refund succeed!')
        return True
    else:
        Notify('refund failed')
        return False


def transferONT(fromacct,toacct,amount):
    """
    transfer ONT
    :param fromacct:
    :param toacct:
    :param amount:
    :return:
    """
    if CheckWitness(fromacct):
        param = [fromacct, toacct, amount]
        res = Invoke(1,contractAddress,'transfer',[param])
        Notify(res)

        if res and res == b'\x01':
            Notify('transfer succeed')
            return True
        else:
            Notify('transfer failed')

            return False

    else:
        Notify('checkWitness failed')
        return False


def done(acct,url):
    """
    finish the domain auction
    :param acct:
    :param url:
    :return:
    """
    currentOwner = Get(ctx,url)
    if currentOwner != selfAddr:
        Notify('not in sell')
        return False
    preOwner = Get(ctx,concat('Original_Owner_',url))
    if preOwner != acct:
        Notify('not owner')
        return False
    amount = Get(ctx,concat('Price_',url))
    param = [selfAddr,acct,amount]
    res = Invoke(1, contractAddress, 'transfer', [param])
    if res and res == b'\x01':
        buyer = Get(ctx,concat('TP_',url))
        Put(ctx,url,buyer)

        Delete(ctx,concat('TP_',url))
        Delete(ctx,concat('Price_',url))
        Delete(ctx,concat('Original_Owner_',url))
        Notify('done succeed!')
        return True
    else:
        Notify('transfer failed')
        return False
