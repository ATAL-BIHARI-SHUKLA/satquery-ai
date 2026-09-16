# RS-LLaVA Server Setup

This document records the exact steps and requirements discovered during the preparation of the RS-LLaVA GPU server environment.

## 1. Remote GPU Requirements Discovered
During verification, the following hardware constraints and environment status were identified:
- **GPU Status:** **FAILED.** No NVIDIA GPU detected on the current environment. `nvidia-smi` failed.
- **CUDA/Driver Status:** **FAILED.** No CUDA environment detected.
- **OS Detected:** Windows 11 (Not Linux as required).
- **Python Version:** 3.13.1 (Official instructions recommend Python 3.10 via Conda).

Because the local environment lacks a GPU and runs Windows, actual GPU execution of RS-LLaVA cannot proceed locally. The following notes document what is required on the *actual* Remote Linux GPU Server.

## 2. Repository Used
- **Source:** [https://github.com/BigData-KSU/RS-LLaVA.git](https://github.com/BigData-KSU/RS-LLaVA.git)
- The repository was successfully cloned and verified locally.

## 3. Dependency Requirements
- Python 3.10 (via Conda)
- `torch` and `torchvision` (must be compiled for CUDA)
- `requirements.txt` from the RS-LLaVA repository

## 4. Models
- **Base Model:** `Intel/neural-chat-7b-v3-3`
- **LoRA Model:** `BigData-KSU/RS-llava-v1.5-7b-LoRA`
*(No heavy model weights were downloaded during this verification step.)*

## 5. Official Inference Entry Point
The official repository does not provide an out-of-the-box HTTP server. It provides a raw Python inference script leveraging `llava.model.builder.load_pretrained_model`.

**Expected Image Input Format:**
- Read via `PIL.Image.open()`
- Preprocessed into tensors via `image_processor.preprocess(..., return_tensors='pt')['pixel_values'][0]`
- Fed into `model.generate` as `.unsqueeze(0).half().cuda()`

**Expected Prompt Format:**
- Utilizes the `llava_v1` conversation template.
- Prepends `DEFAULT_IM_START_TOKEN DEFAULT_IMAGE_TOKEN DEFAULT_IM_END_TOKEN\n` to the raw prompt.

## 6. Commands Successfully Verified (Local)
- `python --version` (Detected 3.13.1)
- `git clone https://github.com/BigData-KSU/RS-LLaVA.git rs-llava-server` (Success)
- `python -m venv rs_llava_env` (Success, though Conda Python 3.10 is recommended for actual deployment)

## 7. What Still Needs to be Done
- **Provision the actual Linux GPU server.**
- Install NVIDIA drivers and CUDA toolkit.
- Install Conda and create a Python 3.10 environment.
- Install `torch`, `torchvision`, and `requirements.txt` inside the Conda environment.
- Write a custom FastAPI/HTTP wrapper around the official inference script to expose the `infer(image_path, question)` API contract expected by SatQuery.
- Download the model weights to the GPU server.
