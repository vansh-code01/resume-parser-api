from fastapi import FastAPI, File, UploadFile
from groq import Groq
import os 
from dotenv import load_dotenv
import pdfplumber
import json

load_dotenv()
app = FastAPI()

@app.get("/")
def home():
    return {"messages" : "Hey everything is working"}

@app.post("/parse-resume")
def pares_resume(file:UploadFile = File(...)):
    result = ""
    with pdfplumber.open(file.file) as f:
        for page in f.pages:
            content = page.extract_text()
            result = result + content
    client = Groq(api_key= os.getenv("GROQ_SECRET_KEY"))
    response = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        messages=[
            {
                "role" : "user",
                "content" : """Extract skills from this resume and return ONLY a JSON object like this:
                            {
                                "technical_skills": [],
                                "soft_skills": [],
                                "languages": []
                            } No extra text. Just the JSON.""" + result 
            }
        ]
    )
    parsed= json.loads(response.choices[0].message.content)
    return parsed
