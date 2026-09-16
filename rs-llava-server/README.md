# RS-LLaVA GPU Server

This is the remote inference server for SatQuery AI. It runs the official RS-LLaVA VQA and captioning models on a dedicated Linux machine with an NVIDIA GPU and CUDA.

## Requirements
- Linux machine
- NVIDIA GPU with CUDA
- Python 3.10+

## Setup Instructions
Do NOT run this server on a machine without a dedicated GPU.

1. **Clone the repo onto your GPU machine.**
2. **Run the setup script:**
   ```bash
   chmod +x setup_gpu.sh
   ./setup_gpu.sh
   ```
   This will install all necessary dependencies, PyTorch, and the official RS-LLaVA package.

3. **Configure the Environment:**
   ```bash
   cp .env.example .env
   # Edit .env and ensure these defaults are correct:
   # MODEL_NAME=BigData-KSU/RS-llava-v1.5-7b-LoRA
   # MODEL_BASE=Intel/neural-chat-7b-v3-3
   # DEVICE=cuda
   # PORT=8001
   ```

## Starting the Server
Start the Uvicorn inference server:
```bash
uvicorn server:app --host 0.0.0.0 --port 8001
```
*Note: The first time you start the server, it will download the 7B model weights (~15GB).*

## Verification & Health Check
Verify the server is running and the model is loaded:
```bash
curl -X GET http://localhost:8001/health
```
You should see:
```json
{
  "status": "ok",
  "model_loaded": true,
  "device": "cuda",
  "model": "BigData-KSU/RS-llava-v1.5-7b-LoRA",
  "cuda_available": true,
  "gpu": "NVIDIA..."
}
```

## First Inference Test
Run the smoke test to perform an inference test directly on the GPU machine:
```bash
python test_gpu_inference.py
```

## Connecting to the SatQuery Backend
Once the server is running on the GPU machine, update your main `backend/.env`:
```env
RS_VQA_ENDPOINT=http://<YOUR_GPU_MACHINE_IP>:8001/infer
```
If you expose the port publicly (e.g. via ngrok or cloud firewall), ensure it is authenticated or network-restricted.
