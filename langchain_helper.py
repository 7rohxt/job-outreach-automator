from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from dotenv import load_dotenv
import chromadb
import json
import os

from few_shots import few_shots
load_dotenv()


def get_llm():
    return ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=1,
        groq_api_key=os.getenv("GROQ_API_KEY")  
    )


def extract_job_description(url: str):
    loader = WebBaseLoader(url)
    page_data = loader.load().pop().page_content

    page_data = "\n".join(
    line.strip() for line in page_data.splitlines() if line.strip()
    )

    llm = get_llm()

    prompt_extract = PromptTemplate(
        input_variables=["page_data"],
        template="""
### Scraped Text from Web url
{page_data}

# Instruction
The scraped text is from the career's page of a website.
Your job is to extract the job postings and return them in JSON format containing the 
following keys: `role`, `experience`, `skills in detail`, and `description`. 
Only return the valid JSON.

### VALID JSON (NO PREAMBLE):
"""
    )

    json_parser = JsonOutputParser() 
    chain_extract = prompt_extract | llm | json_parser 
    job_description = chain_extract.invoke(input={'page_data':page_data})

    return job_description


def resume_to_json (resume_text : str):
    llm = get_llm()

    resume_to_json_prompt = PromptTemplate(
        input_variables=["resume_text"],
        template="""
You are an assistant that converts resumes into structured JSON.
Each section or subheading in the resume should become a key.
The content under each heading should become the value.
Preserve all important details.

Resume Text:
{resume_text}

Return only valid JSON without any extra text.
"""
    )

    json_parser = JsonOutputParser() 
    resume_chain = resume_to_json_prompt | llm | json_parser
    resume = resume_chain.invoke({"resume_text": resume_text})

    return resume


def generate_zeroshot_email(job_description: dict, resume: dict):
    llm = get_llm()

    email_prompt = PromptTemplate(
        input_variables=["job_description", "resume"],
        template="""
You are the candidate described in the resume.

Job Description:
{job_description}

Candidate Resume:
{resume}

Instruction:
Write a concise, professional cold email to the hiring manager that clearly explains
why the candidate is a strong fit for this specific role. 
"""
    )

    email_chain = email_prompt | llm
    email_response = email_chain.invoke(
        {"job_description": job_description, "resume": resume}
    )

    return email_response.content

def setup_vector_db(few_shots):
    chroma_client = chromadb.PersistentClient(path="chroma_db")

    embedding_function = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    collection = chroma_client.get_or_create_collection(name="few_shots")

    ids, documents, metadatas = [], [], []

    for i, example in enumerate(few_shots):
        job_text = json.dumps(example["job_description"], indent=2)
        role = example["job_description"].get("role", "unknown")

        ids.append(f"example_{i}")
        documents.append(job_text)
        metadatas.append({
            "example_id": f"example_{i}",
            "role": role,
            "resume": json.dumps(example["resume"]),
            "email": example["email"]
        })

    collection.add(
        ids=ids, 
        documents=documents, 
        metadatas=metadatas
    )

    return collection


def retrieve_example(query: str, n_results: int = 1):
    chroma_client = chromadb.PersistentClient(path="chroma_db")
    collection = chroma_client.get_collection(name="few_shots")

    results = collection.query(query_texts=[query], n_results=n_results)

    retrieved_job_description = results["documents"][0][0]
    retrieved_meta = results["metadatas"][0][0]

    return {
        "job_description": retrieved_job_description,
        "resume": retrieved_meta["resume"],
        "email": retrieved_meta["email"]
    }


def generate_few_shot_email(job_description: dict, resume: dict, retrieved_example: dict):
    llm = get_llm()

    few_shot_prompt = PromptTemplate(
        input_variables=[
            "retrieved_job_description",
            "retrieved_resume",
            "retrieved_email",
            "job_description",
            "resume"
        ],
        template="""
You are the candidate described in the resume.

### Reference Example
Job Description:
{retrieved_job_description}

Candidate Resume:
{retrieved_resume}

Cold Email:
{retrieved_email}

---

### Task
Now, write a new cold email for the following role:

Job Description:
{job_description}

Candidate Resume:
{resume}

### Guidelines
- Emphasize how the candidate’s skills, frameworks, and technologies align with the job requirements.
- Connect relevant projects/experience to each key requirement in the job description.
- If required years of experience are missing, highlight equivalent projects and achievements instead.
- Keep the email concise, persuasive, and tailored to this job (avoid generic phrasing).
- Limit the email to **around 200 words**.
- End with candidate contact details (email, phone, LinkedIn, GitHub if available).
"""
    )

    email_chain = few_shot_prompt | llm
    email_response = email_chain.invoke({
        "retrieved_job_description": retrieved_example["job_description"],
        "retrieved_resume": retrieved_example["resume"],
        "retrieved_email": retrieved_example["email"],
        "job_description": job_description,
        "resume": resume
    })

    return email_response.content
