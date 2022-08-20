ASCII_DOCTOR_IMAGE := asciidoctor/docker-asciidoctor:latest

docs:
	mkdir -p build/assets
	docker run -v $(PWD):/documents/ $(ASCII_DOCTOR_IMAGE) asciidoctor -o build/README.html -r asciidoctor-diagram README.adoc
	cp -r assets/* build/assets/
.PHONY: build

docs-dev:
	nodemon -e adoc -w ./README.adoc -x make docs
