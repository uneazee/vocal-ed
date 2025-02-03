from flask import Flask, request, jsonify
from flask_cors import CORS
import pyaudio
import speech_recognition as sr
from datasets import load_dataset
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pyttsx3
import numpy as np
import threading
import time

app = Flask(__name__)
CORS(app)

# Initialize (do this ONCE, outside the route)
recognizer = sr.Recognizer()
try:
    ds = load_dataset("microsoft/wiki_qa")
    train_dataset = ds['train']
    print(f"Dataset loaded successfully! {len(train_dataset)} examples")
except Exception as e:
    print(f"Error loading dataset: {e}")
    exit()

try:
    qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
    print("QA pipeline initialized successfully!")
except Exception as e:
    print(f"Error initializing QA pipeline: {e}")
    exit()

vectorizer = TfidfVectorizer()
all_documents = [doc.get('document_title', '') + " " + doc.get('answer', '') for doc in train_dataset]
vectorizer.fit(all_documents)
document_vectors = vectorizer.transform(all_documents)

# Initialize TTS engine (do this ONCE, outside the route)
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)


def find_best_context(question, document_vectors):
    try:
        question_vector = vectorizer.transform([question])
        similarities = cosine_similarity(question_vector, document_vectors)
        most_similar_index = similarities.argmax()
        return all_documents[most_similar_index]
    except Exception as e:
        print(f"Error in find_best_context: {e}")
        return ""

def speak_text(text):
    def _speak():
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Error in TTS: {e}")

    thread = threading.Thread(target=_speak)
    thread.start()

@app.route('/api/process_question', methods=['POST'])
def process_question():
    try:
        start_time = time.time()

        data = request.get_json()
        question = data.get('question')

        if not question:
            return jsonify({'error': 'Question is required'}), 400

        context_start = time.time()
        context = find_best_context(question, document_vectors)
        context_end = time.time()
        print(f"Context: {context}")

        qa_start = time.time()
        result = qa_pipeline(question=question, context=context)
        qa_end = time.time()
        print(f"QA Result: {result}")

        tts_start = time.time()
        speak_text(result['answer'])  # Speak the answer
        tts_end = time.time()

        end_time = time.time()

        print(f"Total time: {end_time - start_time}")
        print(f"Context retrieval time: {context_end - context_start}")
        print(f"QA pipeline time: {qa_end - qa_start}")
        print(f"TTS time: {tts_end - tts_start}")

        return jsonify({'answer': result['answer']})

    except Exception as e:
        print(f"Error processing question: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)