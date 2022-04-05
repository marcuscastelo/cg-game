VENDOR_FOLDER := vendor

.PHONY: install-deps
install-deps:
	$(VENDOR_FOLDER)/install_deps.sh
	pip install -r requirements.txt
		
requirements.txt: save-deps

.PHONY: save_deps
save-deps:
	@echo "Saving dependencies to requirements.txt"
	./save_deps.sh

run: requirements.txt
	sudo python src/main.py