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

requirements.txt: save-deps

.PHONY: save_deps
save-deps:
	@echo "Saving dependencies to requirements.txt"
	./save_deps.sh

run: requirements.txt
	sudo python src/main.py