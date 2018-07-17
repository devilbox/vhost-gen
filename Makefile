# Unix Makefile

# Configuration
SHELL = /bin/sh

MKDIR_P = mkdir -p

BINARY = vhost_gen.py
CONFIG = conf.yml
TPLDIR = templates

all:
	@echo "Nothing to make."
	@echo "Type 'make install' or 'make uninstall'"


help:
	@echo Options
	@echo "   make lint"
	@echo "      Check for python errors"
	@echo ""
	@echo "   make test"
	@echo "      Test vhost-gen"
	@echo ""
	@echo "   make install"
	@echo "      Install everthing (requires sudo or root)"
	@echo ""
	@echo "   make uninstall"
	@echo "      Remove everything (requires sudo or root)"
	@echo ""
	@echo "   make help"
	@echo "      Show this help screen"


lint:
	if pycodestyle --version >/dev/null 2>&1; then pycodestyle -v --max-line-length=100 bin/vhost_gen.py; else echo "not installed"; fi
	if pylint --version >/dev/null 2>&1; then pylint bin/vhost_gen.py; else echo "not installed"; fi
	if flake8 --version >/dev/null 2>&1; then flake8 --max-line-len=100 bin/vhost_gen.py; else echo "not installed"; fi


test:
	./bin/vhost_gen.py -p ./ -n name -t etc/templates/
	./bin/vhost_gen.py -p ./ -n name -t etc/templates/ | grep -v '__'

	./bin/vhost_gen.py -p ./ -n name -t etc/templates/ -c etc/conf.yml
	./bin/vhost_gen.py -p ./ -n name -t etc/templates/ -c etc/conf.yml | grep -v '__'

	./bin/vhost_gen.py -p ./ -n name -t etc/templates/ -c examples/conf.nginx.yml
	./bin/vhost_gen.py -p ./ -n name -t etc/templates/ -c examples/conf.nginx.yml | grep -v '__'

	./bin/vhost_gen.py -p ./ -n name -t etc/templates/ -c examples/conf.apache22.yml
	./bin/vhost_gen.py -p ./ -n name -t etc/templates/ -c examples/conf.apache22.yml | grep -v '__'

	./bin/vhost_gen.py -p ./ -n name -t etc/templates/ -c examples/conf.apache24.yml
	./bin/vhost_gen.py -p ./ -n name -t etc/templates/ -c examples/conf.apache24.yml | grep -v '__'


install:
	@echo "Installing files"
	@echo ""

	@# Create directories
	${MKDIR_P} /etc/vhost-gen
	${MKDIR_P} /etc/vhost-gen/templates

	@# Install binary
	install -m 0755 bin/${BINARY} /usr/bin/${BINARY}

	@# Install configs
	install -m 0644 etc/${CONFIG} /etc/vhost-gen/${CONFIG}
	install -m 0644 etc/${TPLDIR}/*.yml /etc/vhost-gen/${TPLDIR}

	@echo "Installation complete:"
	@echo "----------------------------------------------------------------------"
	@echo ""


uninstall:
	@echo "Removing files"
	@echo ""

	rm -r /etc/vhost-gen
	rm /usr/bin/${BINARY}


	@echo "Uninstallation complete:"
	@echo "----------------------------------------------------------------------"
	@echo ""
