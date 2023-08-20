image:         ## Build the docker image
	docker build --no-cache -t payment-service .

services:      ## Creates necessary services for development
	docker-compose -f ./devops/docker-compose.services.yml up --force-recreate

services-d:    ## Creates necessary services for development in background
	docker-compose -f ./devops/docker-compose.services.yml up -d

services-down:      ## Creates necessary services for development
	docker-compose -f ./devops/docker-compose.services.yml down

dev-run:       ## Run app locally
	docker-compose -f ./devops/docker-compose.yml up --force-recreate

dev-down:      ## Tear down app
	docker-compose -f ./devops/docker-compose.yml down

create-migration:
	docker-compose -f ./devops/docker-compose.yml run server alembic revision --autogenerate -m $(migration_message)

run-migration:
	docker-compose -f ./devops/docker-compose.yml run server alembic upgrade head
