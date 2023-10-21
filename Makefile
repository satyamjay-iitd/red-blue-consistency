redblue:
	docker-compose --profile rb build
	docker-compose --profile rb up

redis:
	docker-compose --profile redis up

both:
	docker-compose --profile all up

clean:
	docker-compose --profile all down
