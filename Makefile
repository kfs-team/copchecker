.PHONY: run
run:
	docker-compose up -d

.PHONY: stop
stop:
	docker-compose stop

.PHONY: run-rebuild
run-rebuild:
	docker-compose up -d --build
