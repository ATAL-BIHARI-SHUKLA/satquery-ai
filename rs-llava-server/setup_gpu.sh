#!/bin/bash
set -e

echo "=================================================="
echo "SatQuery AI - RS-LLaVA GPU Setup Script"
echo "=================================================="

echo "[1/7] Creating Python virtual environment..."
python3 -m venv venv

echo "[2/7] Activating virtual environment..."
source venv/bin/activate

echo "[3/7] Upgrading pip..."
pip install --upgrade pip

echo "[4/7] Installing PyTorch with CUDA support..."
# Install the appropriate PyTorch for CUDA (e.g., cu118 or cu121 based on environment)
# Using default index which usually detects the right version, or specify explicitly if needed.
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo "[5/7] Installing RS-LLaVA server requirements..."
pip install -r requirements.txt

echo "[6/7] Installing official RS-LLaVA package..."
echo "Cloning the official RS-LLaVA repository into a temporary directory..."
git clone https://github.com/KSU-CS-VIMAL/RS-LLaVA.git /tmp/RS-LLaVA
cd /tmp/RS-LLaVA
pip install -e .
pip install -e ".[train]"
pip install flash-attn --no-build-isolation
cd -

echo "[7/7] Verifying CUDA environment..."
python check_environment.py

echo "=================================================="
echo "Setup Complete!"
echo "Please copy .env.example to .env and configure your variables."
echo "Do not download model weights automatically here; they will be loaded dynamically by the server on first startup."
echo "=================================================="
