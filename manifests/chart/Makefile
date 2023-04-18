VERSION ?= 0.0.0

clean:
	rm -rf *.tgz

build: clean
	helm package . --version ${VERSION}

push: build
	helm push ./application-${VERSION}.tgz oci://${REGISTRY}/helm-application

test:
	helm template foo ./ -f values.test.yaml
