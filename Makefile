VENDOR_FOLDER := vendor

.PHONY: install-deps
install-deps:
	$(VENDOR_FOLDER)/install_deps.sh
	pip install -r requirements.txt
		
uninstall-all-packages:
	@echo "WARNING: This will uninstall all packages from your system!"
	@echo "Press enter to continue or CTRL+C to abort."
	@read
	pip uninstall -y $(shell pip freeze | grep -v '^\-e')

run:
	python src/main.py