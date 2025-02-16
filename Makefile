# Variables
PYTHON := python
PIP := $(PYTHON) -m pip
GO := go
FLOWWEAVER_DIR := tests/FloWWeaver

# Default target
all: install test

# Install system dependencies

install-opencv:
	sudo apt update
	sudo apt install -y build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
	sudo apt install -y libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libdc1394-22-dev
	sudo apt install -y libopenexr-dev libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev
	git clone https://github.com/opencv/opencv.git
	git clone https://github.com/opencv/opencv_contrib.git
	cd opencv && git checkout 4.11.0
	cd ../opencv_contrib && git checkout 4.11.0
	cd ..
	mkdir -p opencv/build
	cd opencv/build
	cmake -D CMAKE_BUILD_TYPE=Release \
	      -D CMAKE_INSTALL_PREFIX=/usr/local \
	      -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
	      -D OPENCV_ENABLE_NONFREE=ON \
	      -D BUILD_EXAMPLES=ON ..
	make -j$(nproc)
	sudo make install
	pkg-config --modversion opencv4

install-system-deps: install-opencv


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