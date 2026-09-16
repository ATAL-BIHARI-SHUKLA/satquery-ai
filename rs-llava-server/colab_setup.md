# RS-LLaVA Google Colab Setup Workflow

This document describes the exact workflow to deploy the SatQuery AI RS-LLaVA inference server on Google Colab for testing.

## Prerequisites
1. Open a new Google Colab notebook.
2. Navigate to **Runtime → Change runtime type**.
3. Select **T4 GPU** (or any available NVIDIA GPU) and save.

## 1. Clone the Project
In a new cell, clone the SatQuery repository (or upload the `rs-llava-server` directory).
```bash
!git clone <YOUR_SATQUERY_REPO_URL>
%cd satquery/rs-llava-server
```

## 2. Install Required Dependencies
Run the following commands in a Colab cell to install PyTorch (usually pre-installed with CUDA on Colab), requirements, and the official RS-LLaVA package.

```bash
!pip install --upgrade pip
!pip install -r requirements.txt

# Clone official RS-LLaVA repo and install its package
!git clone https://github.com/KSU-CS-VIMAL/RS-LLaVA.git /tmp/RS-LLaVA
%cd /tmp/RS-LLaVA
!pip install -e .
!pip install -e ".[train]"
!pip install flash-attn --no-build-isolation
%cd /content/satquery/rs-llava-server
```

## 3. Verify CUDA Environment
Check the NVIDIA driver and CUDA availability.
```bash
!nvidia-smi
!python check_environment.py
```

## 4. Configure Environment Variables
Create a `.env` file to configure the server.
```bash
%%writefile .env
MODEL_NAME=BigData-KSU/RS-llava-v1.5-7b-LoRA
MODEL_BASE=Intel/neural-chat-7b-v3-3
DEVICE=cuda
PORT=8001
HOST=0.0.0.0
MAX_NEW_TOKENS=256
```

## 5. Expose the Server (ngrok / localtunnel)
Google Colab does not expose ports publicly by default. 
> **SECURITY WARNING:** Exposing a server publicly via ngrok/localtunnel without authentication allows anyone on the internet to invoke your GPU inference endpoint, potentially incurring high resource usage. Use with caution for testing only.

```bash
# Using localtunnel as an example
!npm install -g localtunnel
# Run localtunnel in the background
!lt --port 8001 --subdomain my-satquery-rs-llava &
```

## 6. Start the Server
Start the Uvicorn inference server. This will download the base model and LoRA weights on the first run.
```bash
!uvicorn server:app --host 0.0.0.0 --port 8001
```

## 7. Test the Server
Once the server says "Model loaded successfully", test the health endpoint using a new cell (or from your local backend).
```bash
!curl -X GET http://localhost:8001/health
```
If using localtunnel, point your local backend `RS_VQA_ENDPOINT` to `https://my-satquery-rs-llava.loca.lt/infer`.
