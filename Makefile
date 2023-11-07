#redblue:
#	docker-compose --profile rb build
#	docker-compose --profile rb up

redblue:
	cd server && GOOS=linux go build -o ./bin/redblue ./cmd/redblue
	server/bin/redblue 7380 &
	server/bin/redblue 7381 &
	sleep 1
	server/bin/redblue 127.0.0.1 7380 127.0.0.1 7381


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
	pkill -9 redblue
