REPO=quay.io/deeptigargb/deeptigargb
VERSION=$(shell git rev-parse HEAD)
PIPELINE_IMAGE=dee_image

build:
	docker build -t $(REPO)/$(PIPELINE_IMAGE):${VERSION} -f Dockerfile ../..

shell: build
	docker run -it --rm $(REPO)/$(PIPELINE_IMAGE):${VERSION} bash

push:
	docker push $(REPO)/$(PIPELINE_IMAGE):${VERSION}

pull:
	docker pull $(REPO)/$(PIPELINE_IMAGE):$(VERSION)

tag-image: pull
	docker tag $(REPO)/$(PIPELINE_IMAGE):$(VERSION) $(REPO)/$(PIPELINE_IMAGE):${IMG_TAG}
	docker push $(REPO)/$(PIPELINE_IMAGE):${IMG_TAG}
