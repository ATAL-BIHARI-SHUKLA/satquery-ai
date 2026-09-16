# Remote-Sensing VQA & Captioning Model Integration

This document outlines the architecture and requirements for integrating a real remote-sensing Vision-Language Model (VLM) like RS-LLaVA into the SatQuery AI system.

## 1. Target Model
The target integration is a **remote-sensing VQA/captioning model** specialized in interpreting satellite and aerial imagery. 

## 2. Expected Inputs & Outputs
- **Expected Input**: 
  - `image_paths`: List of local file paths (typically one image for VQA/Captioning).
  - `query`: A natural-language question or instruction (e.g., "What is the primary land cover here?").
  - `context`: Additional metadata if required.
- **Expected Output**: A textual string containing the generated answer or descriptive caption. The `analyze()` method should format this into a standardized dictionary containing the `status` and `answer`.

## 3. Configuration & Inference
- **Where model weights would be configured**: Model path identifiers, repository names (e.g. HuggingFace repo), or inference API keys should be added to `backend/app/core/config.py` and sourced from the `.env` file.
- **Where inference would happen**: Inside `backend/app/models/base.py` by overriding the `analyze(...)` method of `RemoteSensingVQAModel`. The implementation would load the image using a library like Pillow or OpenCV, tokenize the query, run the forward pass through the VLM, and decode the output.

## 4. How it connects to SpecialistModel
`RemoteSensingVQAModel` inherits from the abstract `SpecialistModel` class. It registers itself to the `ModelRegistry` mapping to the `VQA` and `CAPTIONING` tasks. The adapter provides a unified `analyze()` contract that abstracts the underlying PyTorch/Transformers code away from the rest of the application.

## 5. How unavailable-model fallback currently works
Currently, `RemoteSensingVQAModel.is_available()` returns `False`. 
When the `execute_analysis()` function in `app.services.executor` attempts to invoke the model, it checks this availability flag. Since the model is unavailable, the executor cleanly falls back to its existing mock execution logic (`execute_vqa()`), returning predefined mock responses. This ensures the frontend and API contracts remain unbroken while backend AI capabilities are being provisioned.
