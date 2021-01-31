import json
import sys # to get stdin only
import time
import datetime

"""


"""
# so at the beginning we highly likely need some variables in module scope, let's imagine we are taking that data from some persistent storage like database:
# trx_id = 1000 # we are not using UUID/snowflakes here, but maybe we will use something like last_trx_time = 00.00.00 or timestamp as ID
account = None # as we have strict rule there will be one account and by default it is not initiated with data.
violations = [] # if we have one acc only, we can have one list of current violations on this acc.
transaction_cart = {} # well, most probably we need some sort of in-memory storage for all transactions on the account.
card_overdraft = 0 # just to have another flexible `limit`. 
# card_overdraft limit should be added to the account instance, but then it will be serialized as well and change output,
# so decided to have it outside to not brake examples.
# limits for violations:
trx_limit_high_frequency = 3
trx_limit_high_frequency_time = 120
trx_limit_doubled = 2
trx_limit_doubled_time = 120


# class Receiver:
#     """
#     Class object to work with incoming data
#     """
#     def __init__(self, data):
#         self.data = json.loads(data)
    
#     def __repr__(self):
#         """
#         In case we need to investigate this data object:
#         """
#         return f'< Receiver data: {type(self.data)} {self.data}>'


class Account:
    def __init__(self, data):
        self.account = data['account']
        #self.card_is_active = data['account']['active-card']
        #self.card_limit = int(data['account']['available-limit'])
        self.violations = []
    
    def __repr__(self):
        #return f'< Account card is active: {self.card_is_active} with limit {self.card_limit} and violations {self.violations}>'
        return json.dumps(self, cls=AccountEncoder) # serializer
    
    def get_limit(self):
        #return self.card_limit
        return self.account['available-limit']

    def is_active_card(self):
        #return self.card_is_active
        return self.account['active-card']

    def apply_trx(self, trx):
        self.account['available-limit'] = int(self.account['available-limit']) - trx.get_amount()
        return self.account['available-limit']

    def add_violation(self, violations):
        self.violations = violations
        return f'<current violations: {self.violations}>'

class AccountEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.__dict__


class Transaction:
    def __init__(self, data):
        self.merchant = data['transaction']['merchant']
        self.amount = int(data['transaction']['amount']) # believe it > 0
        self.time = data['transaction']['time']
    
    def __repr__(self):
        return f'<Transaction for {self.amount} to {self.merchant} at {self.time}>'

    def get_amount(self):
        return self.amount
    
    # we need to make conversion from transaction time to timestamp (ts)
    # for future usage ts as ID of trx in transaction_cart.
    def get_ts(self):
        trx_ts = datetime.datetime.strptime(self.time, "%Y-%m-%dT%H:%M:%S.%fZ")
        return trx_ts.timestamp()


def violator(account, trx):
    violations = [] # reset all previous violations

    #limit exceeded:
    if trx.get_amount() > account.get_limit() + card_overdraft:
        violations.append("insufficient-limit")
    #not-init-acc:
    #    violations.append("account-not-init")
    
    #active-card:
    if not account.is_active_card():
        violations.append("card-not-active")
    
    # 3 transactions per 2 minutes:
    # we can have special trx_bucket for transfers for last 120 seconds
    # and do two violation checks against this bucket only
    # to prevent checks to do it twice for all transaction_cart and trx times.
    # so I created here some sort of filtering by `id` field, which we have as timestamp of the transaction:
    recent_trx = [v for x, v in enumerate(transaction_cart) if v > trx.get_ts() - trx_limit_high_frequency_time]
    # then check if in filtered results we have more items than limit:
    if len(recent_trx) >= trx_limit_high_frequency:
        violations.append("high-frequency-small-interval")

    # doubled transaction:
    # as we already have list of recent transactions for 2 minutes,
    # we can use it to go through the list and see if it is doubled or no:
    for tx in recent_trx:
        print(transaction_cart[tx])
        if transaction_cart[tx]['merchant'] == trx.merchant \
        and transaction_cart[tx]['amount'] == trx.amount:
            violations.append("doubled-transaction")
    
    # add all found violations to the acc:
    account.add_violation(violations)
    if not violations:
        return False
    else:
        return True



def startStream():
    global account # we have clue how to work with global
    acc_msg = False
    trx_msg = False
    
    for line in sys.stdin:
        data = json.loads(line)

        try:
            data['account']
            acc_msg = True
            trx_msg = False
        except:
            pass
        try:
            data['transaction']
            trx_msg = True
            acc_msg = False
        except:
            pass

        if acc_msg and not account:
            account = Account(data)
            print(account)

        if trx_msg and account:
            trx = Transaction(data)
            if violator(account, trx):
                print(account)
            else:
                account.apply_trx(trx)
                transaction_cart[trx.get_ts()] = data['transaction']
                print(account)

        if acc_msg and account:
            account.add_violation("account-already-initialized")
            print(account)

        if trx_msg and not account:
            print('{"account-not-initialized"}')
            

if __name__ == "__main__":
    startStream()

"""
TO DO, improvements:
- write tests
- some sort of sequence for transaction_cart, as in current implementation it took timestamp,
     but what if more than 1 transaction came at the exact same time - this case is not covered.
- Some sort of receiver/router of the input data (complete Receiver class)
    to make startStream() look more great

"""