ifneq (,)
.error This Makefile requires GNU Make.
endif

# -------------------------------------------------------------------------------------------------
# Default configuration
# -------------------------------------------------------------------------------------------------
.PHONY: help lint code dist sdist bdist build checkbuild deploy autoformat clean


VERSION = 2.7
BINPATH = bin/
BINNAME = vhost-gen

CONFIG = conf.yml
TPLDIR = templates

FL_VERSION = 0.3
FL_IGNORES = .git/,.github/,*.egg-info,.mypy_cache/

# -------------------------------------------------------------------------------------------------
# Default Target
# -------------------------------------------------------------------------------------------------
help:
	@echo "lint             Lint repository"
	@echo "code             Lint source code"
	@echo "test             Test source code"
	@echo "autoformat       Autoformat code according to Python black"
	@echo "install          Install (requires sudo or root)"
	@echo "uninstall        Uninstall (requires sudo or root)"
	@echo "build            Build Python package"
	@echo "dist             Create source and binary distribution"
	@echo "sdist            Create source distribution"
	@echo "bdist            Create binary distribution"
	@echo "clean            Build"


# -------------------------------------------------------------------------------------------------
# Lint Repository Targets
# -------------------------------------------------------------------------------------------------
lint: _lint-files
lint: _lint-version

.PHONY: _lint-files
_lint-files:
	@echo "# --------------------------------------------------------------------"
	@echo "# Lint files"
	@echo "# -------------------------------------------------------------------- #"
	@docker run --rm $$(tty -s && echo "-it" || echo) -v $(PWD):/data cytopia/file-lint:$(FL_VERSION) file-cr --text --ignore '$(FL_IGNORES)' --path .
	@docker run --rm $$(tty -s && echo "-it" || echo) -v $(PWD):/data cytopia/file-lint:$(FL_VERSION) file-crlf --text --ignore '$(FL_IGNORES)' --path .
	@docker run --rm $$(tty -s && echo "-it" || echo) -v $(PWD):/data cytopia/file-lint:$(FL_VERSION) file-trailing-single-newline --text --ignore '$(FL_IGNORES)' --path .
	@docker run --rm $$(tty -s && echo "-it" || echo) -v $(PWD):/data cytopia/file-lint:$(FL_VERSION) file-trailing-space --text --ignore '$(FL_IGNORES)' --path .
	@docker run --rm $$(tty -s && echo "-it" || echo) -v $(PWD):/data cytopia/file-lint:$(FL_VERSION) file-utf8 --text --ignore '$(FL_IGNORES)' --path .
	@docker run --rm $$(tty -s && echo "-it" || echo) -v $(PWD):/data cytopia/file-lint:$(FL_VERSION) file-utf8-bom --text --ignore '$(FL_IGNORES)' --path .

.PHONY: _lint-version
_lint-version:
	@echo "# -------------------------------------------------------------------- #"
	@echo "# Check version config"
	@echo "# -------------------------------------------------------------------- #"
	@VERSION_VHOSTGEN=$$( grep -E '^VERSION = "v?[.0-9]+(-\w+)?"' $(BINPATH)$(BINNAME) | awk -F'"' '{print $$2}' || true ); \
	VERSION_SETUP=$$( grep version= setup.py | awk -F'"' '{print $$2}' || true ); \
	if [ "$${VERSION_VHOSTGEN}" != "$${VERSION_SETUP}" ]; then \
		echo "[ERROR] Version mismatch"; \
		echo "bin/vhost-gen:  $${VERSION_VHOSTGEN}"; \
		echo "setup.py:       $${VERSION_SETUP}"; \
		exit 1; \
	else \
		echo "[OK] Version match"; \
		echo "bin/vhost-gen: $${VERSION_VHOSTGEN}"; \
		echo "setup.py:      $${VERSION_SETUP}"; \
		exit 0; \
	fi \


# -------------------------------------------------------------------------------------------------
# Lint Code Targets
# -------------------------------------------------------------------------------------------------
code: _code-pycodestyle
code: _code-pydocstyle
code: _code-pylint
code: _code-black
code: _code-mypy

.PHONY: _code-pycodestyle
_code-pycodestyle:
	@echo "# -------------------------------------------------------------------- #"
	@echo "# Check pycodestyle"
	@echo "# -------------------------------------------------------------------- #"
	docker run --rm $$(tty -s && echo "-it" || echo) -v $(PWD):/data cytopia/pycodestyle --show-source --show-pep8 $(BINPATH)$(BINNAME)

.PHONY: _code-pydocstyle
_code-pydocstyle:
	@echo "# -------------------------------------------------------------------- #"
	@echo "# Check pydocstyle"
	@echo "# -------------------------------------------------------------------- #"
	docker run --rm $$(tty -s && echo "-it" || echo) -v $(PWD):/data cytopia/pydocstyle $(BINPATH)$(BINNAME)

.PHONY: _code-pylint
_code-pylint:
	@echo "# -------------------------------------------------------------------- #"
	@echo "# Check pylint"
	@echo "# -------------------------------------------------------------------- #"
	docker run --rm $$(tty -s && echo "-it" || echo) -v $(PWD):/data cytopia/pylint --rcfile=setup.cfg $(BINPATH)$(BINNAME)

.PHONY: _code-black
_code-black:
	@echo "# -------------------------------------------------------------------- #"
	@echo "# Check black"
	@echo "# -------------------------------------------------------------------- #"
	docker run --rm $$(tty -s && echo "-it" || echo) -v ${PWD}:/data cytopia/black -l 100 --check --diff $(BINPATH)$(BINNAME)

.PHONY: _code-mypy
_code-mypy:
	@echo "# -------------------------------------------------------------------- #"
	@echo "# Check mypy"
	@echo "# -------------------------------------------------------------------- #"
	docker run --rm $$(tty -s && echo "-it" || echo) -e PIP_ROOT_USER_ACTION=ignore -v ${PWD}:/data -w /data cytopia/mypy \
		--config-file setup.cfg \
		--install-types \
		--non-interactive \
		$(BINPATH)$(BINNAME)


# -------------------------------------------------------------------------------------------------
# Test Targets
# -------------------------------------------------------------------------------------------------

test:
	@$(MAKE) --no-print-directory _test FILE=check-errors-normal.sh
	@$(MAKE) --no-print-directory _test FILE=check-errors-reverse.sh
	@$(MAKE) --no-print-directory _test FILE=check-errors-template-normal.sh
	@$(MAKE) --no-print-directory _test FILE=check-errors-template-reverse.sh


_test:
	@echo "--------------------------------------------------------------------------------"
	@echo " Test $(FILE)"
	@echo "--------------------------------------------------------------------------------"
	docker run \
		--rm \
		$$(tty -s && echo "-it" || echo) \
		-v $(PWD):/data \
		-w /data \
		python:$(VERSION)-alpine \
		sh -c "pip install -r requirements.txt \
			&& apk add bash make \
			&& make install \
			&& tests/$(FILE)"


# -------------------------------------------------------------------------------------------------
# Build Targets
# -------------------------------------------------------------------------------------------------

dist: sdist bdist

sdist:
	docker run \
		--rm \
		$$(tty -s && echo "-it" || echo) \
		-v $(PWD):/data \
		-w /data \
		-u $$(id -u):$$(id -g) \
		python:$(VERSION)-alpine \
		python setup.py sdist

bdist:
	docker run \
		--rm \
		$$(tty -s && echo "-it" || echo) \
		-v $(PWD):/data \
		-w /data \
		-u $$(id -u):$$(id -g) \
		python:$(VERSION)-alpine \
		python setup.py bdist_wheel --universal

build:
	docker run \
		--rm \
		$$(tty -s && echo "-it" || echo) \
		-v $(PWD):/data \
		-w /data \
		-u $$(id -u):$$(id -g) \
		python:$(VERSION)-alpine \
		python setup.py build

checkbuild:
	docker run \
		--rm \
		$$(tty -s && echo "-it" || echo) \
		-v $(PWD):/data \
		-w /data \
		python:$(VERSION)-alpine \
		sh -c "pip install twine \
		&& twine check dist/*"


# -------------------------------------------------------------------------------------------------
# Publish Targets
# -------------------------------------------------------------------------------------------------

deploy:
	docker run \
		--rm \
		$$(tty -s && echo "-it" || echo) \
		-v $(PWD):/data \
		-w /data \
		python:$(VERSION)-alpine \
		sh -c "pip install twine \
		&& twine upload dist/*"


# -------------------------------------------------------------------------------------------------
# Misc Targets
# -------------------------------------------------------------------------------------------------

autoformat:
	docker run \
		--rm \
		$$(tty -s && echo "-it" || echo) \
		-v $(PWD):/data \
		-w /data \
		cytopia/black -l 100 $(BINPATH)$(BINNAME)
clean:
	-rm -rf $(BINNAME).egg-info/
	-rm -rf dist/
	-rm -rf build/

install:
	@echo "Installing files"
	@echo ""
	@# Create directories
	mkdir -p /etc/vhost-gen
	mkdir -p /etc/vhost-gen/templates
	@# Install binary
	install -m 0755 $(BINPATH)/$(BINNAME) /usr/bin/$(BINNAME)
	@# Install configs
	install -m 0644 etc/$(CONFIG) /etc/vhost-gen/$(CONFIG)
	install -m 0644 etc/$(TPLDIR)/*.yml /etc/vhost-gen/$(TPLDIR)
	@echo "Installation complete:"
	@echo "----------------------------------------------------------------------"
	@echo ""

uninstall:
	@echo "Removing files"
	@echo ""
	rm -r /etc/vhost-gen
	rm /usr/bin/$(BINNAME)
	@echo "Uninstallation complete:"
	@echo "----------------------------------------------------------------------"
	@echo ""
