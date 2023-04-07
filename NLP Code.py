import openai
import json
import os
import pandas as pd
from difflib import SequenceMatcher

# Set your OpenAI API key
openai.api_key = ('XXX')
'''Retrieve API key from https://platform.openai.com/account/api-keys and replace XXX with the
API Key'''

# Set up the GPT-3.5 Turbo model
model_engine = "text-davinci-003"
prompt = "What is the answer to the following question?"

# Set the file paths for the Excel sheets
student_file_path = os.path.join(os.path.dirname(__file__), "student_qna.xlsx")
teacher_file_path = os.path.join(os.path.dirname(__file__), "teacher_qna.xlsx")

# Check if the student Excel sheet exists
if os.path.isfile(student_file_path):
    # Load the existing sheet
    student_df = pd.read_excel(student_file_path)
    # Check if the sheet has columns "Question" and "Answer"
    if "Question" not in student_df.columns or "Answer" not in student_df.columns:
        # If not, create a new DataFrame with those columns
        student_df = pd.DataFrame(columns=["Question", "Answer"])
else:
    # If the sheet does not exist, create a new DataFrame with columns "Question" and "Answer"
    student_df = pd.DataFrame(columns=["Question", "Answer"])

# Check if the teacher Excel sheet exists
if os.path.isfile(teacher_file_path):
    # Load the existing sheet
    teacher_df = pd.read_excel(teacher_file_path)
    # Check if the sheet has columns "Question" and "Answer"
    if "Question" not in teacher_df.columns or "Answer" not in teacher_df.columns:
        # If not, create a new DataFrame with those columns
        teacher_df = pd.DataFrame(columns=["Question", "Answer"])
else:
    # If the sheet does not exist, create a new DataFrame with columns "Question" and "Answer"
    teacher_df = pd.DataFrame(columns=["Question", "Answer"])

# Prompt the student to ask questions until they are done
while True:
    # Prompt the student for their question
    student_question = input("What is your question? (Type 'done' to exit) ")
    if student_question.lower() == "done":
        break
    
    # Check for similar questions in the teacher's DataFrame
    similarity_threshold = 0.9
    similar_questions = teacher_df[teacher_df["Question"].apply(lambda x: SequenceMatcher(None, x.lower(), student_question.lower()).ratio() >= similarity_threshold)]
    if len(similar_questions) > 0:
        # If there is a similar question in the teacher's DataFrame, use the answer from the first matching question
        print(similar_questions.iloc[0]["Answer"])
        student_df = pd.concat([student_df, pd.DataFrame({"Question": student_question, "Answer": similar_questions.iloc[0]["Answer"]}, index=[0])], ignore_index=True)
    else:
        # If there is no similar question in the teacher's DataFrame, ask OpenAI for the answer and add it to the student DataFrame
        response = openai.Completion.create(engine=model_engine, prompt=prompt + "\n" + student_question, max_tokens=1024, n=1, stop=None, temperature=0.7)
        answer = response.choices[0].text.strip()
        student_df = pd.concat([student_df, pd.DataFrame({"Question": student_question, "Answer": answer}, index=[0])], ignore_index=True)
        print(answer)
        
    # Save the updated DataFrames to their respective Excel sheets
    student_df.to_excel(student_file_path, index=False)
    teacher_df.to_excel(teacher_file_path, index=False)
