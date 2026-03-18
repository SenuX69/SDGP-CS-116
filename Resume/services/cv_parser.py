import pdfplumber
from docx import Document
import re

#Extracting text from PDF document

def extract_pdf_text(file_path):
    
    text = ""

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"
    
    return text


# Extracting text from Word Documents

def extract_docx_text(file_path):

    doc = Document(file_path)

    text = "\n".join([p.text for p in doc.paragraphs])

    return text

# Extracting user's personal email 

def extract_email(text):

    emails = re.findall(r'\S+@\S+',text)

    if emails:
        return emails[0]
    
    return None

# Extracting user phone number

def extract_phone(text):

    phones = re.findall(r'\+?\d[\d\s-]{8,15}', text)

    if phones:
        return phones[0]
    
    return None


# Extracting user's Skills

def extract_skills(text):

    skills_database = ["Python", "Java","React", "SQL", 
                       "FastAPI", "Machine Learning", 
                       "JavaScript", "HTML", "CSS", "Node.js", 
                       "C++", "C#","TypeScript"]
    
    found_skills = []
    text_lower = text.lower()

    for skill in skills_database:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return found_skills


# Extracting user's educational qualification type

def extract_education(text):

    education_type = ["bachelor","bsc","beng","msc","master","diploma"]

    education = []

    lines = text.split("\n")

    for line in lines:
        for keyword in education_type:
            if keyword in line.lower():
                education.append(line.strip())

    return education[:3]


def parse_cv_text(text):

    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills(text)
    education = extract_education(text)

    return{
        "email": email,
        "phone": phone,
        "skills": skills,
        "education": education
    }
