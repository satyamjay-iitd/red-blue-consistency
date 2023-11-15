![Generated Button](https://github.com/satyamjay-iitd/red-blue-consistency/blob/image-data/badge.svg)

# Comparing RedBlue Consistency VS Strict Consistency
[RedBlue Consistency](https://www.usenix.org/system/files/conference/osdi12/osdi12-final-162.pdf)

## Redis configuration (Sync Replication)
Three Redis instances, one master and 2 replicas

Start the cluster using `make redis`

This will start the cluster with the following configuration:

- Master listening on 6379
- Replica 1 listening on 6380
- Replica 2 listening on 6381

### Load custom lua functions on Redis

`` cat mylib.lua | redis-cli -p 6379 -x FUNCTION LOAD REPLACE``

## Redis configuration (Async Replication)
- Run all the commands given above
- Change `RDS_REP_IN_SYNC` to `False` in `.env`


## Our configuration (RedBlue Consistent)
- Run `make redblue`

This will start the cluster with the following configuration:
- Master listening on 7379
- Replica 1 listening on 7380
- Replica 2 listening on 7381



## Benchmarks

### Prerequisites

#### Build & Install RedBlue Client
- Install Poetry using `curl -sSL https://install.python-poetry.org | python3 -`
- Build Library using `cd rb_client && poetry build`
- Install Library using `pip install rb_client/dist/redblue-0.1.0.tar.gz`

#### Install other dependencies
- `pip install -r benchmark/requirements.txt`

### Running Word Count
``cd benchmark``

``python -m cli wc redis|redblue [text_file_path]``

``python -m cli wc --help``

### Bank
``cd benchmark``

``python -m cli bank redis|redblue [num_txns] [withdrawal_prob] [deposit_prob] [interest_rate]``

``python -m cli bank --help``

- num_txns:- Controls size of the input
- Withdrawal is a red operation, increasing its probability will slow down the entire operation
- AccrueInterest probability is inferred: `1 - wp - dp`
- interest rate is taken as `rate*10000`, so if you want `1%` interest rate give `0.01 * 10000 = 10` 
- Keep the interest rate small for high num_txns otherwise balance will explode


### Set
``cd benchmark``

``python -m cli bank redis|redblue [N_OPS] [ADD_P]``

``python -m cli bank --help``

- N_OPS:- Controls size of the input
- ADD_P:- Controls probability of add ops(blue)
- Remove probability is inferred: `1 - add_p`
- Remove is a red operation, increasing its probability will slow down the entire operation
