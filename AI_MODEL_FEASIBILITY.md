# AI Model Feasibility Audit

This document outlines the current system capabilities and evaluates the feasibility of replacing the mocked AI analysis with a real Vision-Language Model (VLM).

## CURRENT ENVIRONMENT
- **Python Version**: 3.13.1
- **Available RAM**: ~7.6 GB (Total System RAM ~8GB)
- **Available GPU**: None detected (CPU-only environment)
- **CUDA Availability**: Not available
- **PyTorch Installation**: Missing in all virtual environments (`.venv` and `rs_llava_env`)
- **AI/ML Dependencies**: None installed
- **`rs-llava-server` Directory**: Exists and contains inference scripts/server templates, but **no** model checkpoints.
- **Local Model Checkpoints**: None
- **`.env` Configuration**: Contains `RS_VQA_MODEL_NAME=BigData-KSU/RS-llava-v1.5-7b-LoRA` but `RS_VQA_ENDPOINT` is empty.

## EXISTING AI ARCHITECTURE
- **`app/services/router.py`**: Uses simple keyword rules to classify user queries into `TaskType`.
- **`app/services/executor.py`**: Attempts to fetch a model from the registry. If unavailable, falls back to Python-based logic (for location development) or hardcoded string mocks (for VQA/captioning).
- **`app/models/registry.py`**: Maintains a list of `SpecialistModel` instances. Currently initialized with placeholder model classes.
- **`app/models/base.py`**: Defines a `RemoteSensingVQAModel` that attempts to call an external inference endpoint via a `RemoteInferenceClient`.
- **Where to Connect**: A real model should be implemented by creating a new `SpecialistModel` subclass in `app/models/base.py` (or a dedicated adapter file), overriding the `analyze()` method, and registering it in `app/models/registry.py`.

## AVAILABLE MODEL OPTIONS

### A. RS-LLaVA / Remote-Sensing VLM Locally
- **Can it run?**: **NO**
- **Model Size**: 7 Billion parameters
- **Required Hardware**: 16GB+ VRAM (or ~8GB VRAM with 4-bit quantization)
- **Image+NLP Support**: Yes
- **Remote-Sensing Suitability**: Excellent (fine-tuned specifically for this)
- **Integration**: `RemoteSensingVQAModel` is already designed to hit an RS-LLaVA endpoint.
- **API Key**: No
- **Main Limitation**: The current hardware (CPU-only, 8GB System RAM) physically cannot load or run a 7B parameter model. Attempting to run it on CPU will crash due to Out-Of-Memory (OOM) errors or take 15+ minutes per query.

### B. Smaller Open-Source VLM Locally (e.g., Moondream2, Phi-3-Vision)
- **Can it run?**: **Barely / Unusable**
- **Model Size**: ~1.8B to 3.8B parameters
- **Required Hardware**: 4GB - 8GB RAM
- **Image+NLP Support**: Yes
- **Remote-Sensing Suitability**: Low to Moderate (general purpose, no remote-sensing specific tuning)
- **Integration**: Requires a custom adapter in `base.py`.
- **API Key**: No
- **Main Limitation**: Even small models running on CPU will consume all available system RAM, severely degrading the performance of the OS, the Vite frontend server, and the FastAPI backend. CPU inference will still be painfully slow (minutes per query).

### C. Cloud VLM / API (e.g., Gemini 1.5 Pro / Flash, GPT-4o)
- **Can it run?**: **YES**
- **Model Size**: N/A (Offloaded to cloud)
- **Required Hardware**: None (runs over HTTP)
- **Image+NLP Support**: Yes
- **Remote-Sensing Suitability**: Moderate to High (State-of-the-art zero-shot capabilities on satellite imagery, though lacks specialized multi-spectral band understanding).
- **Integration**: Highly compatible. A new `CloudVLMAdapter` inheriting from `SpecialistModel` can be added to `base.py` and registered.
- **API Key**: Required
- **Main Limitation**: Requires an internet connection and an active API key.

### D. Existing Model in Project
- None exists.

## RECOMMENDED ARCHITECTURE
Given the severe hardware constraints (No GPU, 8GB RAM), running **any** local Large Vision-Language Model is physically impossible without crashing the system or facing unacceptable latency.

**Recommendation: Option C (Cloud VLM / API)**
We should integrate a cloud-based VLM (e.g., Gemini API) by creating a `CloudVLMAdapter` in the backend.

## BLOCKERS
- The system lacks the hardware (GPU/RAM) to run the `BigData-KSU/RS-llava-v1.5-7b-LoRA` model specified in the `.env` file.
- The `rs-llava-server` code relies on PyTorch and CUDA, which are not installed and cannot be fully utilized on this machine.

## NEXT SINGLE IMPLEMENTATION TASK
1. Choose a Cloud VLM provider (e.g., Google Gemini).
2. Create a new model adapter class in `backend/app/models/base.py` that implements the `SpecialistModel` interface and calls the Cloud VLM API.
3. Register this new adapter in `backend/app/models/registry.py` to seamlessly replace the mocked AI responses without altering the frontend or router architecture.
