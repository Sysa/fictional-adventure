import unittest
import json
from app import Account

data = '{"account": {"active-card": true, "available-limit": 100}}'
acc_data = '{"account": {"active-card": true, "available-limit": 100}, "violations": []}'
data_json = json.loads(data)

class TestAccount(unittest.TestCase):
    def setUp(self):
        self.account = Account(data_json)

    def test_account(self):
        # this test is not the best way to perform check, but at least it checks for quality of strings and json objects it produce:
        self.assertEqual(str(self.account), str(acc_data))
        self.assertEqual(json.loads(str(self.account)), json.loads(acc_data))

    def test_get_acc_limit(self):
        self.assertEqual(self.account.get_limit(), json.loads(acc_data)['account']['available-limit'])

    def test_acc_card(self):
        self.assertEqual(self.account.is_active_card(), json.loads(acc_data)['account']['active-card'])


if __name__ == '__main__':
    unittest.main()
