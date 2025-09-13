install:
	bash scripts/install.sh

install.force:
	bash scripts/install.sh --rebuild

# Usage:
# make install.autoupdate MINUTES=5
install.autoupdate:
	bash scripts/install.sh --autoupdate $(MINUTES)

uninstall:
	bash scripts/uninstall.sh

update-database:
	docker run --rm -v $(shell pwd):/app -w /app techwatch-app python techwatch_service.py
