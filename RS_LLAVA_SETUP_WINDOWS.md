# RS-LLaVA GPU Server Setup Guide (Windows)

Yeh guide un Windows laptops ke liye hai jinke paas **NVIDIA GPU** hai aur jahan SatQuery AI ka frontend aur backend pehle se run ho raha hai.

## Pre-requisites
- NVIDIA GPU (Kam se kam 8GB-16GB VRAM recommended).
- NVIDIA Drivers installed hone chahiye (`nvidia-smi` command chalni chahiye).
- Naya terminal (Command Prompt) open karein `satquery-ai` root folder ke andar.

---

### Step 1: AI ke liye alag environment banayein
Isse aapke backend ka environment kharab nahi hoga.
```bash
python -m venv rs_llava_env
```

### Step 2: Environment ko chalu (activate) karein
```cmd
.\rs_llava_env\Scripts\activate
```
*(Aap dekhenge ki terminal line ke shuru mein `(rs_llava_env)` likha aa jayega)*

### Step 3: GPU Server ke folder mein jaayein
```bash
cd rs-llava-server
```

### Step 4: PyTorch CUDA install karein (Sabse zaroori step)
Yeh NVIDIA GPU ko use karne ke liye zaroori hai.
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Step 5: Server ki baaki zaruratein install karein
```bash
pip install -r requirements.txt
```

### Step 6: Original RS-LLaVA ka model code install karein
Commands ko line-by-line copy karke chalne dein:
```bash
git clone https://github.com/KSU-CS-VIMAL/RS-LLaVA.git
cd RS-LLaVA
pip install -e .
cd ..
```

### Step 7: GPU Server Start karein
```bash
uvicorn server:app --host 0.0.0.0 --port 8001
```
> **Dhyan dein:** Jab aap ise pehli baar chalayenge, toh yeh internet se ~15GB ka model background mein download karega. Ise pura hone dein. Jab "Model loaded successfully" likha aa jaye, matlab server ready hai!

---

### Step 8: Backend ko batayein ki AI Server kahan chal raha hai (Last Step)

Kyunki aapka backend aur AI server ek hi laptop par chal rahe hain, toh apne backend ke `.env` file ko open karein aur yeh line add kar dein:
```env
RS_VQA_ENDPOINT=http://127.0.0.1:8001/infer
```

Bas! Ab jab aap SatQuery AI ke map par click karke query bhejenge, toh aapki application directly is GPU server ko image bhejegi aur real AI se answers laakar dikhayegi.
