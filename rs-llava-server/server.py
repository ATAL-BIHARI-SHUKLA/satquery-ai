from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import io
import base64
import os
from PIL import Image

# Official RS-LLaVA Imports (commented out or conditionally imported to avoid crashing if not installed)
try:
    import torch
    from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN, DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN
    from llava.conversation import conv_templates, SeparatorStyle
    from llava.model.builder import load_pretrained_model
    from llava.utils import disable_torch_init
    from llava.mm_utils import tokenizer_image_token, get_model_name_from_path, KeywordsStoppingCriteria
    MODEL_LIBS_AVAILABLE = True
except ImportError:
    MODEL_LIBS_AVAILABLE = False

app = FastAPI(title="RS-LLaVA Inference Server")

# Global variables for model state
tokenizer = None
model = None
image_processor = None
context_len = None
model_loaded = False
load_error = None

class InferRequest(BaseModel):
    model: str
    question: str
    image: str  # Can be a local path or a base64 encoded string

@app.on_event("startup")
def load_model():
    global tokenizer, model, image_processor, context_len, model_loaded, load_error
    
    if not MODEL_LIBS_AVAILABLE:
        load_error = "RS-LLaVA libraries (llava) are not installed in this environment."
        return

    try:
        # Configuration
        model_path = os.getenv("MODEL_NAME", 'BigData-KSU/RS-llava-v1.5-7b-LoRA')
        model_base = os.getenv("MODEL_BASE", 'Intel/neural-chat-7b-v3-3')
        device = os.getenv("DEVICE", 'cuda')
        
        disable_torch_init()
        model_name = get_model_name_from_path(model_path)
        
        tokenizer, model, image_processor, context_len = load_pretrained_model(model_path, model_base, model_name, device_map=device)
        model_loaded = True
    except Exception as e:
        load_error = str(e)
        model_loaded = False

@app.get("/health")
def health_check():
    cuda_available = False
    gpu_name = None
    try:
        import torch
        if torch.cuda.is_available():
            cuda_available = True
            gpu_name = torch.cuda.get_device_name(0)
    except ImportError:
        pass
    
    return {
        "status": "ok",
        "model_loaded": model_loaded,
        "device": os.getenv("DEVICE", "cuda"),
        "model": os.getenv("MODEL_NAME", "BigData-KSU/RS-llava-v1.5-7b-LoRA"),
        "cuda_available": cuda_available,
        "gpu": gpu_name,
        "load_error": load_error
    }

@app.post("/infer")
def infer(request: InferRequest):
    if not request.question:
        raise HTTPException(status_code=400, detail="Missing question")
    if not request.image:
        raise HTTPException(status_code=400, detail="Missing image")

    if not model_loaded:
        return {
            "status": "model-unavailable",
            "message": f"Model not loaded. Error: {load_error}",
            "answer": None
        }

    try:
        # Decode the image
        if os.path.isfile(request.image):
            image_mem = Image.open(request.image).convert('RGB')
        else:
            try:
                img_data = base64.b64decode(request.image)
                image_mem = Image.open(io.BytesIO(img_data)).convert('RGB')
            except Exception as decode_err:
                raise HTTPException(status_code=400, detail="Image must be a valid file path or a base64 encoded string.")

        image_tensor = image_processor.preprocess(image_mem, return_tensors='pt')['pixel_values'][0]

        cur_prompt = request.question
        if model.config.mm_use_im_start_end:
            cur_prompt = f"{DEFAULT_IM_START_TOKEN} {DEFAULT_IMAGE_TOKEN} {DEFAULT_IM_END_TOKEN}\n{cur_prompt}"
        else:
            cur_prompt = f"{DEFAULT_IMAGE_TOKEN}\n{cur_prompt}"

        conv_mode = 'llava_v1'
        conv = conv_templates[conv_mode].copy()
        conv.append_message(conv.roles[0], cur_prompt)
        conv.append_message(conv.roles[1], None)
        prompt = conv.get_prompt()
        
        device = os.getenv("DEVICE", "cuda")
        
        if device == "cuda":
            input_ids = tokenizer_image_token(prompt, tokenizer, IMAGE_TOKEN_INDEX, return_tensors='pt').unsqueeze(0).cuda()
            img_tensor_kwargs = {"images": image_tensor.unsqueeze(0).half().cuda()}
        else:
            input_ids = tokenizer_image_token(prompt, tokenizer, IMAGE_TOKEN_INDEX, return_tensors='pt').unsqueeze(0).to(device)
            img_tensor_kwargs = {"images": image_tensor.unsqueeze(0).to(device)}

        stop_str = conv.sep if conv.sep_style != SeparatorStyle.TWO else conv.sep2
        keywords = [stop_str]
        stopping_criteria = KeywordsStoppingCriteria(keywords, tokenizer, input_ids)

        max_new_tokens = int(os.getenv("MAX_NEW_TOKENS", "256"))

        with torch.inference_mode():
            output_ids = model.generate(
                input_ids,
                do_sample=True,
                temperature=0.2,
                top_p=None,
                num_beams=1,
                no_repeat_ngram_size=3,
                max_new_tokens=max_new_tokens,
                use_cache=True,
                **img_tensor_kwargs
            )

        input_token_len = input_ids.shape[1]
        outputs = tokenizer.batch_decode(output_ids[:, input_token_len:], skip_special_tokens=True)[0]
        outputs = outputs.strip()

        return {
            "status": "success",
            "answer": outputs,
            "model": request.model,
            "device": device,
            "confidence": None,
            "metadata": {
                "task": "vqa"
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
