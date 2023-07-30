ifneq (,$(wildcard ./.env))
    include .env
    export
endif ## Export Enviornment variables

image:         ## Build the docker image
	docker build --no-cache -t payment-service .

dev-run:       ## Run app locally
	docker run -v ${VOLUME_PATH}/:/app/ --name payment-server -p 8000:8000 payment-service

dev-down:       ## Run app locally
	docker rm -f payment-server

