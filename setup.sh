#!/bin/bash

echo "====================================="
echo "Podcast Clipper Bot Setup"
echo "====================================="

echo
echo "Checking Python..."
python3 --version || { echo "Install Python 3.9+"; exit 1; }

echo
echo "Creating virtual environment..."
python3 -m venv venv

echo
echo "Activating virtual environment..."
source venv/bin/activate

echo
echo "Upgrading pip..."
pip install --upgrade pip

echo
echo "Installing dependencies..."
pip install openai-whisper pyyaml torch torchvision torchaudio

echo
echo "Checking FFmpeg..."
ffmpeg -version || echo "WARNING: Install FFmpeg (brew install ffmpeg)"

echo
echo "Setup complete!"