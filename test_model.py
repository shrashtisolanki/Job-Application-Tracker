
from models.resume_matcher import calculate_similarity

resume = """
I am a Python developer with knowledge of
machine learning, deep learning, SQL,
Pandas, NumPy and Flask.
I have developed data analysis projects.
"""

job_description = """
We are looking for a Python developer
with experience in Python, SQL,
machine learning, Flask and data analysis.
"""

score = calculate_similarity(
    resume,
    job_description
)

print("\nResume Matching Results")
print("-----------------------")

print("Resume:", resume)

print("Job Description:", job_description)

print("Similarity Score:", score, "%")
