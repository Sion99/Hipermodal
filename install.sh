#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR"

# Check if project exists
if [ -d "hipermodal" ]; then
    echo "Hipermodal already exists. Delete it or install in a different directory."
    exit 1
fi

echo "Cloning git repository..."

# Clone git repository
git clone https://github.com/Sion99/Hipermodal.git hipermodal
cd hipermodal

# Install portaudio using Homebrew
echo "Installing portaudio via Homebrew..."
brew install portaudio

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate
source .venv/bin/activate

# Install required libraries
echo "Installing required dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Deactivate
deactivate

echo "Installation complete. To run this program, execute run.sh"
