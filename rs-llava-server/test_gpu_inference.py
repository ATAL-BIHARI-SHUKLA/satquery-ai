import os
import sys
import torch
import requests
import time

def main():
    print("==================================================")
    print("RS-LLaVA GPU Smoke Test")
    print("==================================================")
    
    # 1. Check CUDA Availability
    if not torch.cuda.is_available():
        print("ERROR: CUDA is not available. This script is intended for GPU machines only.")
        print("Please run this on a machine with an NVIDIA GPU and CUDA configured.")
        sys.exit(1)
        
    print("CUDA is available! GPU:", torch.cuda.get_device_name(0))
    
    # Check if a test image exists
    test_image_path = "../backend/uploads/sample.jpg" # Change to a valid image if needed
    if not os.path.exists(test_image_path):
        print(f"\nNo test image found at {test_image_path}.")
        print("Please provide a valid remote-sensing image file (e.g. sample.jpg) in the correct path")
        print("or update the 'test_image_path' variable in this script to point to an image.")
        sys.exit(1)
        
    # We will send a request to the local server assuming it's running
    SERVER_URL = "http://127.0.0.1:8001"
    
    print("\n[1/2] Checking Server Health...")
    try:
        health_resp = requests.get(f"{SERVER_URL}/health", timeout=10)
        health_resp.raise_for_status()
        health_data = health_resp.json()
        print(f"Health status: {health_data['status']}")
        print(f"Model Loaded: {health_data['model_loaded']}")
        if not health_data.get('model_loaded', False):
            print("ERROR: Server is running but model is not loaded.")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Could not connect to the inference server at {SERVER_URL}.")
        print("Ensure you have started the server with: uvicorn server:app --host 0.0.0.0 --port 8001")
        print(f"Details: {e}")
        sys.exit(1)
        
    print("\n[2/2] Running Inference...")
    payload = {
        "image": test_image_path,
        "question": "What kind of land cover is shown in this image?"
    }
    
    try:
        start_time = time.time()
        resp = requests.post(f"{SERVER_URL}/infer", json=payload, timeout=120)
        resp.raise_for_status()
        result = resp.json()
        end_time = time.time()
        
        print("\n--- INFERENCE RESULT ---")
        print(f"Status: {result.get('status')}")
        print(f"Answer: {result.get('answer')}")
        print(f"Time Taken: {end_time - start_time:.2f} seconds")
        print("------------------------")
        
    except requests.exceptions.RequestException as e:
        print(f"\nERROR: Inference request failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
