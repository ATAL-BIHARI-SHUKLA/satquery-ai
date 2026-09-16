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
