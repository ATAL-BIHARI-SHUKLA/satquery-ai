import sys
import os

def check_env():
    print("Environment Check:")
    print("-" * 40)
    print(f"Python: {sys.version}")
    
    try:
        import torch
        print(f"PyTorch: {torch.__version__}")
        
        cuda_available = torch.cuda.is_available()
        print(f"CUDA Available: {cuda_available}")
        
        if cuda_available:
            print(f"CUDA Version: {torch.version.cuda}")
            for i in range(torch.cuda.device_count()):
                print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
    except ImportError:
        print("PyTorch: NOT INSTALLED")
        
    try:
        import transformers
        print(f"Transformers: {transformers.__version__}")
    except ImportError:
        print("Transformers: NOT INSTALLED")
        
    try:
        import peft
        print(f"PEFT: {peft.__version__}")
    except ImportError:
        print("PEFT: NOT INSTALLED")
        
    try:
        import accelerate
        print(f"Accelerate: {accelerate.__version__}")
    except ImportError:
        print("Accelerate: NOT INSTALLED")

if __name__ == "__main__":
    check_env()
