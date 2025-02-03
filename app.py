from flask import Flask, request, jsonify
from flask_cors import CORS
import faiss
import numpy as np
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
import pyttsx3
import threading

app = Flask(__name__)
CORS(app)

# Load dataset once at startup
dataset = load_dataset("microsoft/wiki_qa")['train']
print("Dataset loaded successfully!")

# Load Sentence Transformer Model
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Sentence Transformer model loaded!")

# Precompute embeddings for dataset questions
dataset_questions = [entry['question'] for entry in dataset]
dataset_question_embeddings = model.encode(dataset_questions)

# Convert embeddings to FAISS index
embedding_dim = dataset_question_embeddings.shape[1]
faiss_index = faiss.IndexFlatL2(embedding_dim)
faiss_index.add(dataset_question_embeddings)
print("FAISS index built!")

def find_best_answer(user_question):
    user_embedding = model.encode([user_question]).astype(np.float32)
    _, best_index = faiss_index.search(user_embedding, 1)
    best_index = int(best_index[0][0])
    return dataset[best_index]['answer']

def initialize_tts():
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1)
    return engine

def speak_text(text):
    def _speak():
        try:
            engine = initialize_tts()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")
    threading.Thread(target=_speak, daemon=True).start()

@app.route('/api/process_question', methods=['POST'])
def process_question():
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        if not question:
            return jsonify({'error': 'Question is required'}), 400

        answer = find_best_answer(question)
        speak_text(answer)
        return jsonify({'answer': answer})
    except Exception as e:
        print(f"Error processing question: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)