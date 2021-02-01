# transaction authorizer

## Description

Application `authorizer` authorizes a transaction for specific account. The application handles two kinds of operations:

- Account creation
- Transaction authorization

Each operation should be valid json object passed as string to the application's input. One operation == one line.

The program should not rely on any external database. Internal state should be handled
by an explicit in-memory structure. State is to be reset at application start.

The following limitations and business rules applied in the authorizer app:

- Account:
  - The application will deal with just one account ()
  - Once created, the account should not be updated or recreated
  - No transaction should be accepted without a properly initialized account: `account-not-initialized`
- Transactions:
  - All monetary values are positive integers using a currency without cents
  - Transactions must arrive in chronological order
  - No transaction should be accepted when the card is not active: `card-not-active`
  - The transaction amount should not exceed available limit: `insufficient-limit`
  - There should not be more than 3 transactions on a 2 minute interval: `high-frequency-small-interval`
  - There should not be more than 1 similar transactions (same amount and
merchant) in a 2 minutes interval: doubled-transaction
- Another limitations:
  - Please assume input parsing errors will not happen.
  - Violations of the business rules are not considered to be errors as they are expected to happen and should be listed in the outputs's violations field as described on the output schema in the examples. That means the program execution should continue normally after any violation.

Application tested on Python versions `3.8.2` and `3.8.7`, so python is required to run the app.

---

## Under the hood (application design)

Few moments about application design should be described in the details:

- `startStream` - function that dealing with the stdin input and routes requests to particular class/method.
- `Account` class and it's methods are used primely to deal with all account-related data.
- `AccountEncoder` - class helper to represent account instance as json object.
- `Transaction` - class for transactions, can convert transaction time to timestamp for future usage during violation checks.
- `violator` - function, that taking account and transaction as input and fills in violations for the account based on that transaction and transaction's history from `transaction_cart` dictionary (used as in-memory storage, instead of database). Most challenging part was about `high-frequency-small-interval` and `doubled-transaction` violations, which based on time and count of recent transactions. As we have condition *"Transactions must arrive in chronological order"* - I used time as timestamp ID, which helps me to filter out recent transactions by time and deal with that business rules in efficient way.

---

## Examples of usage

### Account creation

```sh
λ cat acc_test
{"account": {"active-card": true, "available-limit": 100}}
{"account": {"active-card": true, "available-limit": 99}}
{"account": {"active-card": true, "available-limit": 90}}

λ python app.py < acc_test
{"account": {"active-card": true, "available-limit": 100}, "violations": []}
{"account": {"active-card": true, "available-limit": 100}, "violations": "account-already-initialized"}
{"account": {"active-card": true, "available-limit": 100}, "violations": "account-already-initialized"}
```

### Transaction authorization

```sh
λ cat trx_test
{"account": {"active-card": true, "available-limit": 100}}
{"transaction": {"merchant": "Burger King", "amount": 10, "time": "2019-02-13T10:00:00.000Z"}}
{"transaction": {"merchant": "Habbib's", "amount": 10, "time": "2019-02-13T11:00:00.000Z"}}
{"transaction": {"merchant": "McDonalds", "amount": 10, "time": "2019-02-13T11:01:00.000Z"}}
{"transaction": {"merchant": "KFC", "amount": 65, "time": "2019-02-13T11:01:01.000Z"}}
{"transaction": {"merchant": "Habbib's", "amount": 10, "time": "2019-02-13T11:01:10.000Z"}}
{"transaction": {"merchant": "Golden Cock Pub", "amount": 10, "time": "2019-02-13T11:05:20.000Z"}}
{"transaction": {"merchant": "Bank commission", "amount": 3, "time": "2019-02-13T13:05:20.000Z"}}

λ python app.py < trx_test
{"account": {"active-card": true, "available-limit": 100}, "violations": []}
{"account": {"active-card": true, "available-limit": 90}, "violations": []}
{"account": {"active-card": true, "available-limit": 80}, "violations": []}
{"account": {"active-card": true, "available-limit": 70}, "violations": []}
{"account": {"active-card": true, "available-limit": 5}, "violations": []}
{"account": {"active-card": true, "available-limit": 5}, "violations": ["insufficient-limit", "high-frequency-small-interval", "doubled-transaction"]}
{"account": {"active-card": true, "available-limit": 5}, "violations": ["insufficient-limit"]}
{"account": {"active-card": true, "available-limit": 2}, "violations": []}
```

## Usage

To start the application, go to it's work dir and run: `python app.py`

To stop the application - enter to the input new line char `\n` or `\r\n`

## Testing

Application has unit an integration tests, here is few steps examples to run tests against authorizer:

### To run all existing tests at once

At working directory run `python -m unittest discover -v` to discover all test cases and run it. Output:

```sh
λ python -m unittest discover -v
test_acc_card (test_account.TestAccount) ... ok
test_account (test_account.TestAccount) ... ok
test_get_acc_limit (test_account.TestAccount) ... ok
test_app_input_run (test_integration.TestAppInput) ... ok
test_transaction_amount (test_transaction.TestTransaction) ... ok
test_transaction_ts (test_transaction.TestTransaction) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.101s

OK
```

## Build application as docker container

To build docker container with the authorizer application on the board, use command `docker build . -t authorizer:0.1`. It will run building process and create image with tag `authorizer:0.1`, based on Dockerfile.

output:
```sh
Sending build context to Docker daemon  109.1kB
Step 1/4 : FROM python:3.8
3.8: Pulling from library/python
b9a857cbf04d: Pull complete
d557ee20540b: Pull complete
3b9ca4f00c2e: Pull complete
667fd949ed93: Pull complete
4ad46e8a18e5: Pull complete
381aea9d4031: Pull complete
8a9e78e1993b: Pull complete
9eff4cbaa677: Pull complete
c3c6df49b780: Pull complete
Digest: sha256:9a6b07ef1ecb923abfc444cf90d8bda47d5ae54bda1337e346bf596201b4eb29
Status: Downloaded newer image for python:3.8
 ---> 4d53664a7025
Step 2/4 : WORKDIR /authorizer
 ---> Running in b361d17ed3ff
Removing intermediate container b361d17ed3ff
 ---> 785220a692d9
Step 3/4 : COPY . .
 ---> d3647b5553b9
Step 4/4 : CMD [ "python", "./app.py" ]
 ---> Running in c0126dafb142
Removing intermediate container c0126dafb142
 ---> d1ceb4aa3cb5
Successfully built d1ceb4aa3cb5
Successfully tagged authorizer:0.1
```

Use `docker image ls` command to see your local images.

### Run application as container

To run container (successful image build required), use command `docker run -d -it authorizer:0.1`

Pay attention, that you need to run container with `it` flag to make it running in interactive tty terminal. Otherwise docker engine will not wait for input for the app and conatiner will immediately die just after it's creation.

Use `docker ps` command to see your running containers.

### Testing application inside docker container

To have ability to run application tests inside containerized pipeline, test cases were also included to the the image.

See steps below to run tests inside container:

```sh
λ docker ps | grep authorizer
8f9de7a86d9b        authorizer:0.1      "python ./app.py"   2 minutes ago       Up 2 minutes
```

```sh
λ docker exec -it 8f9de7a86d9b python -m unittest discover -v -t /authorizer
test_acc_card (test_account.TestAccount) ... ok
test_account (test_account.TestAccount) ... ok
test_get_acc_limit (test_account.TestAccount) ... ok
test_app_input_run (test_integration.TestAppInput) ... ok
test_transaction_amount (test_transaction.TestTransaction) ... ok
test_transaction_ts (test_transaction.TestTransaction) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.038s

OK
```
