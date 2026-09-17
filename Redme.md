# commond for run frontend

1. to enter frontend forlder:
   cd frontend

2. to install frontend packages if not exist:
   npm install

3. to run frontend:
   npm run dev

# commond for run backend

1. बैकएंड फोल्डर में जाने के लिए:
   cd backend

2. वर्चुअल एनवायरनमेंट एक्टिवेट करने के लिए:
   .\.venv\Scripts\Activate

3. पैकेज इनस्टॉल करने के लिए (अगर पहले से नहीं किए हैं):
   pip install -r requirements.txt

4. बैकएंड सर्वर को रन करने के लिए:
   uvicorn app.main:app --reload

# commond for setup rs_llava_env (पहली बार सेटअप के लिए)

1. नया वर्चुअल एनवायरनमेंट बनाने के लिए:
   python -m venv rs_llava_env

2. एनवायरनमेंट एक्टिवेट करने के लिए:
   .\rs_llava_env\Scripts\activate

3. सर्वर फोल्डर में जाने के लिए:
   cd rs-llava-server

4. सारे पैकेज इनस्टॉल करने के लिए:
   pip install -r requirements.txt

# commond for run rs-llava-server (रेगुलर रन के लिए)

1. सर्वर फोल्डर में जाने के लिए:
   cd rs-llava-server

2. वर्चुअल एनवायरनमेंट एक्टिवेट करने के लिए:
   ..\rs_llava_env\Scripts\activate

3. सर्वर को रन करने के लिए:
   uvicorn server:app --host 0.0.0.0 --port 8001

# shortcut to start all services (Frontend + Backend + LLM Server)

1. सबसे आसान तरीका (बिना टर्मिनल के):
   प्रोजेक्ट फोल्डर (`satquery-ai`) में जाएँ और `start_all.bat` फाइल पर डबल-क्लिक करें।

2. या फिर टर्मिनल (PowerShell) से रन करने के लिए (मेन फोल्डर में रहते हुए):
   .\start_all.bat
