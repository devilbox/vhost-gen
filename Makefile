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
	@echo "   make install"
	@echo "      Install everthing (requires sudo or root)"
	@echo ""
	@echo "   make uninstall"
	@echo "      Remove everything (requires sudo or root)"
	@echo ""
	@echo "   make help"
	@echo "      Show this help screen"


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
