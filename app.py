from fastapi import FastAPI, File, UploadFile
from groq import Groq
import os 
from dotenv import load_dotenv
import pdfplumber
import json
from database import engine, Session, User, Base, Job
from fastapi import Form
import ast

load_dotenv()
app = FastAPI()

@app.get("/")
def home():
    return {"messages" : "Hey everything is working"}

@app.post("/parse-resume")
def pares_resume(
    file:UploadFile = File(...),
    name: str = Form(...),
    email: str = Form(...)
    ):
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
    new_user = User(
        name = name,
        email = email,
        skills = str(parsed)
    )
    session = Session()
    session.add(new_user)
    session.commit()
    session.close()
    return parsed

@app.post("/add-job")
def add_job(
    title : str = Form(...),
    company : str = Form(...),
    location: str = Form(...),
    description: str = Form(...),
    email: str = Form(...)
):
    new_job = Job(
        title = title,
        company = company,
        location = location,
        description = description,
        email = email
    )
    session = Session()
    session.add(new_job)
    session.commit()
    session.close()
    return {"Message":"Job Created Successfully"}

@app.get("/match-job/{user_id}")
def match_job(user_id: int):
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()

    jobs = session.query(Job).all()
    print("User skills:", user.skills)  # add this
    print("Job description:", jobs[0].description) 
    
    matched = []
    skills_dict = ast.literal_eval(user.skills)
    user_skills_list = []
    for key in skills_dict:
        user_skills_list += skills_dict[key]

    for job in jobs:
        for skills in user_skills_list:
            if skills.lower() in job.description.lower():
                matched.append(job)
                break
    session.close()
    return matched
