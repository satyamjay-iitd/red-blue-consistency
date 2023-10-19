## Our configuration
### Coming soon

## Redis configuration to compare against

3 Redis instances, one master and 2 replicas

Start the cluster using `docker compose up`

This will start the cluster with the following configuration:

- Master listening on 6379
- Replica 1 listening on 6380
- Replica 2 listening on 6381

## Running Benchmarks
``cd benchmark``

### Word Count 
``python cli.py wc redis [text_file]``

``python cli.py wc redblue [text_file]``

