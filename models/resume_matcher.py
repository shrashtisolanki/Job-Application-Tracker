
import pymupdf
import re
import os
import numpy as np

from sentence_transformers import SentenceTransformer


# Load model only once
_model = None

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_model():
    global _model

    if _model is None:
        print("Loading Deep Learning model...")
        _model = SentenceTransformer(MODEL_NAME)
        print("Model loaded successfully!")

    return _model


# Extract text from PDF resume
def extract_resume_text(pdf_path):

    if not os.path.exists(pdf_path):
        raise FileNotFoundError("Resume PDF not found.")

    text = ""

    with pymupdf.open(pdf_path) as document:

        for page in document:
            text += page.get_text() + "\n"

    text = re.sub(r"\s+", " ", text).strip()

    if len(text) < 30:
        raise ValueError(
            "No readable text found. Please upload a text-based PDF resume."
        )

    return text


# Divide long text into smaller chunks
def split_text(text, words_per_chunk=180):

    words = text.split()

    chunks = []

    for i in range(0, len(words), words_per_chunk):

        chunk = " ".join(
            words[i:i + words_per_chunk]
        )

        chunks.append(chunk)

    return chunks


# Generate one embedding for the complete document
def generate_embedding(text):

    model = load_model()

    chunks = split_text(text)

    embeddings = model.encode(
        chunks,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    # Average chunk embeddings
    document_embedding = np.mean(embeddings, axis=0)

    # Normalize final embedding
    norm = np.linalg.norm(document_embedding)

    if norm == 0:
        raise ValueError("Unable to generate text embedding.")

    return document_embedding / norm


# Calculate resume and job similarity
def calculate_similarity(resume_text, job_description):

    if not resume_text.strip():
        raise ValueError("Resume text is empty.")

    if not job_description.strip():
        raise ValueError("Job description is empty.")

    resume_embedding = generate_embedding(resume_text)

    job_embedding = generate_embedding(job_description)

    similarity = np.dot(
        resume_embedding,
        job_embedding
    )

    # Convert cosine similarity into a readable score
    score = max(0, min(100, similarity * 100))

    return round(float(score), 2)


# Identify skills in resume and job description
SKILLS = [
    "python",
    "java",
    "c++",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "html",
    "css",
    "javascript",
    "react",
    "node.js",
    "flask",
    "django",
    "machine learning",
    "deep learning",
    "data science",
    "data analysis",
    "pandas",
    "numpy",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "excel",
    "power bi",
    "tableau",
    "git",
    "github",
    "aws",
    "docker"
]


def extract_skills(text):

    text = text.lower()

    found_skills = []

    for skill in SKILLS:

        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(skill)
            + r"(?![a-z0-9])"
        )

        if re.search(pattern, text):

            found_skills.append(skill)

    return found_skills


# Complete resume analysis
def analyze_resume(pdf_path, job_description):

    resume_text = extract_resume_text(pdf_path)

    score = calculate_similarity(
        resume_text,
        job_description
    )

    resume_skills = extract_skills(resume_text)

    required_skills = extract_skills(job_description)

    matched_skills = [
        skill for skill in required_skills
        if skill in resume_skills
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill not in resume_skills
    ]

    return {
        "match_score": score,
        "resume_skills": resume_skills,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "resume_text": resume_text
    }
