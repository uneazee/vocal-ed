import pyaudio
import speech_recognition as sr
from datasets import load_dataset
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pyttsx3
import threading

# Initialize speech recognizer
recognizer = sr.Recognizer()

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

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)

# Function to convert text to speech
def speak_text(text):
    try:
        engine.say(text)
        engine.runAndWait()  # Ensure speech is processed immediately
    except Exception as e:
        print(f"Error in TTS: {e}")

# Function to listen and process speech
def listen_and_process():
    with sr.Microphone() as source:
        print("Please ask a question...")
        while True:
            try:
                # Adjust for ambient noise and listen for speech
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

                # Recognize speech using Google Speech Recognition API
                text = recognizer.recognize_google(audio)
                print(f"Recognized Text: {text}")

                # Find the most relevant context from the dataset
                context = find_best_context(text, ds['train'])

                # Get the answer from the QA pipeline
                try:
                    result = qa_pipeline(question=text, context=context)
                    print(f"Question: {text}")
                    print(f"Answer: {result['answer']}")

                    # Speak the answer back to the user
                    speak_text(result['answer'])

                except Exception as e:
                    print(f"Error in QA pipeline: {e}")

            except sr.UnknownValueError:
                print("Sorry, I didn't catch that. Please repeat.")
            except sr.RequestError:
                print("Could not request results from Google Speech Recognition service; check your network connection.")

# Run the listen and process function in a separate thread for continuous listening
listener_thread = threading.Thread(target=listen_and_process)
listener_thread.daemon = True  # Daemonize thread to exit when main program exits
listener_thread.start()

# Keep the main program running while the listener thread is working
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Program terminated.")
