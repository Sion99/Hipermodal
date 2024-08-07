#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR"

# Check if project exists
if [ -d "hipermodal" ]; then
    echo "\nHipermodal already exists. Delete it or install in diffrent directory.\n"
    exit 1
fi

echo "\nCloning git repository...\n"

# Clone git repository
git clone https://github.com/Sion99/Hipermodal.git hipermodal
cd hipermodal

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "\nCreating virtual environment...\n"
    python3 -m venv .venv
fi

# Activate
source .venv/bin/activate

# Install required libraries
echo "\nInstalling required dependencies...\n"
pip install --upgrade pip
pip install -r requirements.txt

# Deactivate
deactivate

echo "\nInstallation complete. To run this program, excute run.sh\n"