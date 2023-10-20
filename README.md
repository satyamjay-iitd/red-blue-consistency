# Comparing RedBlue Consistency VS Strict Consistency
[RedBlue Consistency](https://www.usenix.org/system/files/conference/osdi12/osdi12-final-162.pdf)

## Redis configuration (Strict Consistent) to compare against

Three Redis instances, one master and 2 replicas

Start the cluster using `make redis`

This will start the cluster with the following configuration:

- Master listening on 6379
- Replica 1 listening on 6380
- Replica 2 listening on 6381

## Our configuration (RedBlue Consistent)
Start the cluster using `make redblue`

Start both redis and rb in one command using `make both`

Stop all instances using `make clean`


### Loading custom lua functions on Redis

`` cat mylib.lua | redis-cli -p 6379 -x FUNCTION LOAD REPLACE``

## Running Benchmarks
``cd benchmark``

``pip install -r requirements.txt``

### Word Count 
``python -m cli wc redis|redblue [text_file]``

``python -m cli wc --help``

### Bank
``python -m cli bank redis|redblue [num_txns] [withdrawl_prob] [deposit_prob] [interest_rate]``

``python -m cli bank --help``
