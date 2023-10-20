## Our configuration
### Coming soon

## Redis configuration to compare against

Three Redis instances, one master and 2 replicas

Start the cluster using `docker compose up`

This will start the cluster with the following configuration:

- Master listening on 6379
- Replica 1 listening on 6380
- Replica 2 listening on 6381

### Loading custom lua functions on Redis

`` cat mylib.lua | redis-cli -p 6379 -x FUNCTION LOAD REPLACE``

## Running Benchmarks
``cd benchmark``

``pip install -r requirements.txt``

### Word Count 
``python -m cli wc redis [text_file]``

``python -m cli wc redblue [text_file]``

``python -m cli wc --help``

### Bank
``python -m cli bank redis num_transactions withdrawl_prob deposit_prob interest_rate``

``python -m cli bank redblue num_transactions withdrawl_prob deposit_prob interest_rate``

``python -m cli bank --help``
