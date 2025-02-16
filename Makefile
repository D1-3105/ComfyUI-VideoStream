# Variables
PYTHON := python
PIP := $(PYTHON) -m pip
GO := go
FLOWWEAVER_DIR := tests/FloWWeaver
CWD = $(pwd)
# Default target
all: install test

# Install system dependencies

erase-opencv-build:
	cd $CWD
	rm -rf gocv

install-opencv:
	git clone https://github.com/hybridgroup/gocv.git
	cd gocv
	git checkout -b v0.38.0
	make install
	pkg-config --modversion opencv4

install-system-deps: install-opencv erase-opencv-build


# Install Python dependencies
install-python-deps:
	$(PIP) install --upgrade pip
	$(PIP) install flake8 pytest
	if [ -f requirements.txt ]; then $(PIP) install -r requirements-test.txt; fi

# Install ComfyUI node
install_comfyui_node:
	$(PYTHON) install.py

# Lint with flake8
lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Run tests
test:
	pytest tests

# Install everything
install: install-system-deps install-python-deps install_comfyui_node

# Clean build artifacts
clean:
	rm -rf $(FLOWWEAVER_DIR)/FloWWeaver.exe
	$(GO) clean -modcache

.PHONY: all install install-system-deps install-python-deps install_comfyui_node lint test clean