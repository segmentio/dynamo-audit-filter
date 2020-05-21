PROJECT = dynamo-audit-filter
FUNCTION = $(PROJECT)
REGION = us-west-2

.PHONY: deps
deps:
	@echo "Install Deps"

.PHONY: test
test:
	@echo "Perform Tests"

.PHONY: clean
clean:
	rm -f -r build/*
	rm -f -r packages/*

.PHONY: build
build: clean
	mkdir -p build/
	mkdir -p packages/
	zip -r build/$(PROJECT).zip source/*
	docker run -v $(shell pwd)/:/root/ python:3.7 pip3 install -r /root/source/requirements.txt --root /root/packages/
	cp -r ./packages/usr/local/lib/python3.7/site-packages/* ./build/
	cp -r ./source/. ./build
	cd ./build && zip -r ../build/${PROJECT}.zip .


.PHONY: publish
publish:
	buildkite-agent artifact upload ../build/dynamo-audit-filter.zip
