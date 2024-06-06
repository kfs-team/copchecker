.PHONY: run
make run:
	docker-compose up -d

.PHONY: stop
make stop:
	docker-compose stop
