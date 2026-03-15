import pdfplumber
from groq import Groq    
import os
from dotenv import load_dotenv
import json

load_dotenv()

result = ""
with pdfplumber.open('Vansh_RESUME.pdf') as f:
    for page in f.pages:
        content = page.extract_text()
        result  = result + content
    # print(result)

client = Groq(api_key=os.getenv("GROQ_SECRET_KEY"))
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages =[
        {
            "role" : "user",
            "content" : """Extract skills from this resume and return ONLY a JSON object like this:
                        {
                            "technical_skills": [],
                            "soft_skills": [],
                            "languages": []
                        } No extra text. Just the JSON.""" + result
        },
    ]
)
# print(response)
parsed =json.loads(response.choices[0].message.content) 
print(parsed)

with open("data.json",'w') as f:
    f.write(json.dumps(parsed, indent=4))