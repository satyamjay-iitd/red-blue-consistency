redblue:
	docker-compose --profile rb build
	docker-compose --profile rb up

redis:
	docker-compose --profile redis up

redis-raft:
	docker-compose --profile redis-raft up -d
	sleep 3
	redis-cli -p 6379 raft.cluster init
	redis-cli -p 6380 RAFT.CLUSTER JOIN redis-raft-master:6379
	redis-cli -p 6381 RAFT.CLUSTER JOIN redis-raft-master:6379


both:
	docker-compose --profile all up

clean:
	docker-compose --profile all down
