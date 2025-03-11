.PHONY: default
default: run

.PHONY: setup-env
setup-env:
	test -f .env || cp sample.env .env

.PHONY: run
run: setup-env
	test -d .venv || python -m venv .venv
	. .venv/bin/activate && \
	python -m pip install --upgrade pip && \
	python -m pip install -r requirements.txt
	PYTHONPATH=. .venv/bin/python PingMonitor.py

.PHONY: clean
clean:
	rm -rf .venv \
	       __pycache__ \
	       app/__pycache__ \
	       .env
	python -m venv .venv
	. .venv/bin/activate && \
	python -m pip install --upgrade pip && \
	python -m pip install --no-cache -r requirements.txt
	PYTHONPATH=. .venv/bin/python PingMonitor.py