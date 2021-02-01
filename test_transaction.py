import unittest
import json
import time
import datetime
from app import Transaction

"""
TO DO:
- move `data` to separate file
"""

data = [
    '{"transaction": {"merchant": "McDonalds", "amount": 10, "time": "2019-02-13T11:01:01.000Z"}}',
    '{"transaction": {"merchant": "KFC Berlin", "amount": 20, "time": "2019-02-13T11:02:02.000Z"}}',
    '{"transaction": {"merchant": "Pizza Hut", "amount": 30, "time": "2019-02-13T11:03:03.000Z"}}'
]

class TestTransaction(unittest.TestCase):
    def test_transaction_amount(self):
        for line in data:
            line = json.loads(line)
            self.trx = Transaction(line)
            self.assertEqual(self.trx.get_amount(), int(line['transaction']['amount']))

    def test_transaction_ts(self):
        for line in data:
            line = json.loads(line)
            self.trx = Transaction(line)
            trx_ts = datetime.datetime.strptime(line['transaction']['time'], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
            self.assertEqual(self.trx.get_ts(), trx_ts)


if __name__ == '__main__':
    unittest.main()
