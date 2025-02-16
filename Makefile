# Variables
PYTHON := python
PIP := $(PYTHON) -m pip
GO := go
FLOWWEAVER_DIR := tests/FloWWeaver

# Default target
all: install test

# Install system dependencies
install-system-deps:
	$(PIP) install opencv-python
	sudo apt-get update
	sudo add-apt-repository ppa:opencv/opencv-4.8 -y
	sudo apt-get install -y \
			pkg-config \
			libopencv-dev \
			libopencv-contrib-dev \
			libopencv-core-dev \
			libopencv-highgui-dev \
			build-essential \
			cmake
	pkg-config --modversion opencv4


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