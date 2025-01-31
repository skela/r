ROD_VERSION=$(shell cat setup.json | jq --raw-output '"\(.version)"')

.PHONY: build
build:
	docker build -t rod:$(ROD_VERSION) . --build-arg USER_ID=1000 --build-arg GROUP_ID=1000
	docker tag rod:$(ROD_VERSION) skela/rod:$(ROD_VERSION)
	docker tag rod:$(ROD_VERSION) rod:latest
	docker tag rod:$(ROD_VERSION) skela/rod:latest

.PHONY: push
push:
	docker login
	docker push skela/rod:$(ROD_VERSION)
	docker push skela/rod:latest

.PHONY: pull
pull:
	docker pull skela/rod:latest
