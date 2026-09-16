import os

class ModelSettings:
    RS_VQA_MODEL_NAME: str = os.getenv("RS_VQA_MODEL_NAME", "BigData-KSU/RS-llava-v1.5-7b-LoRA")
    RS_VQA_ENDPOINT: str = os.getenv("RS_VQA_ENDPOINT", "")
    RS_VQA_API_KEY: str = os.getenv("RS_VQA_API_KEY", "")
    RS_VQA_TIMEOUT: int = int(os.getenv("RS_VQA_TIMEOUT", "120"))

model_settings = ModelSettings()
