import shutil
import tkinter as tk
from tkinter import filedialog
import speech_recognition as sr
from datasets import load_dataset
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pyttsx3
import os

# Open a file dialog for the user to select a file
root = tk.Tk()
root.withdraw()  # Hide the root window

file_path = filedialog.askopenfilename(initialdir="C:/Users/justx/Downloads", title="Select an Audio File")

# Check if a file was selected
if file_path:
    print(f"File selected: {file_path}")
    try:
        with open(file_path, "rb") as f:
            file_content = f.read()
        print("File uploaded successfully!")
    except Exception as e:
        print(f"Error reading the file: {e}")
        exit()  # Stop execution if file reading fails
else:
    print("No file selected.")
    exit()  # Stop execution if no file is selected

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Try to process audio file
file = file_path  # Use the selected file
try:
    with sr.AudioFile(file) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
    print(f"Recognized Text: {text}")
except Exception as e:
    print(f"Error processing audio: {e}")
    exit()  # Stop execution if audio processing fails

# Load the Microsoft WikiQA dataset
try:
    ds = load_dataset("microsoft/wiki_qa")
    print("Dataset loaded successfully!")
except Exception as e:
    print(f"Error loading dataset: {e}")
    exit()  # Stop execution if dataset fails to load

# Initialize QA pipeline (corrected to use question-answering pipeline)
try:
    qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
    print("QA pipeline initialized successfully!")
except Exception as e:
    print(f"Error initializing QA pipeline: {e}")
    exit()  # Stop execution if pipeline fails to initialize

# Function to find the most similar context from the dataset
def find_best_context(question, dataset):
    """
    Finds the document in the dataset most similar to the question.
    """
    vectorizer = TfidfVectorizer()

    # Fit the vectorizer to all documents in the dataset
    all_documents = [doc.get('document_title', '') + " " + doc.get('answer', '') for doc in dataset]
    vectorizer.fit(all_documents)

    # Transform the question and all documents into vectors
    question_vector = vectorizer.transform([question])
    document_vectors = vectorizer.transform(all_documents)

    # Calculate cosine similarities between the question and all documents
    similarities = cosine_similarity(question_vector, document_vectors)

    # Get the index of the most similar document
    most_similar_index = similarities.argmax()

    # Return the text of the most similar document
    return all_documents[most_similar_index]

# Find the most relevant context
context = find_best_context(text, ds['train'])

# Get the answer from the QA model
try:
    # Using the correct 'question' and 'context' as inputs to the QA pipeline
    result = qa_pipeline(question=text, context=context)
    print(f"Question: {text}")
    print(f"Answer: {result['answer']}")
except Exception as e:
    print(f"Error in QA pipeline: {e}")
    exit()  # Stop execution if QA model fails

# Initialize TTS engine
engine = pyttsx3.init()

# Set properties (optional)
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)

# Define the output audio file path
output_audio_path = os.path.join("C:/Users/justx/Downloads", "response.mp3")

# Convert the generated text to speech (TTS)
try:
    engine.save_to_file(result['answer'], output_audio_path)
    engine.runAndWait()  # Ensure the speech is processed and saved
    print(f"Audio file saved successfully at: {output_audio_path}")
except Exception as e:
    print(f"Error saving audio file: {e}")

# File to simulate download by copying to another location (optional)
destination_path = "C:/Users/justx/Downloads/response.mp3"  # Or another folder

# Simulate file download by copying the saved audio file
try:
    shutil.copy(output_audio_path, destination_path)
    print(f"File downloaded to: {destination_path}")
except Exception as e:
    print(f"Error downloading file: {e}")