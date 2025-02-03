import React, { useState, useEffect } from 'react';
import useSpeechToText from 'react-hook-speech-to-text';
import './App.css';

function App() {
    const [userAnswer, setUserAnswer] = useState(localStorage.getItem('userAnswer') || '');
    const [botAnswer, setBotAnswer] = useState('');
    const [error, setError] = useState(null);
    const [isRecording, setIsRecording] = useState(false);
    
    const {
        results,
        startSpeechToText,
        stopSpeechToText,
        isRecording: useSpeechToTextIsRecording,
        error: speechError,
    } = useSpeechToText({
        continuous: true,
        useLegacyResults: false,
    });

    useEffect(() => {
        if (results.length > 0) {
            const text = results.map((result) => result.transcript).join(' ');
            setUserAnswer(text);
            localStorage.setItem('userAnswer', text);
        }
    }, [results]);

    useEffect(() => {
        setIsRecording(useSpeechToTextIsRecording);
    }, [useSpeechToTextIsRecording]);

    const handleRecordButtonClick = () => {
        if (isRecording) {
            stopSpeechToText();
        } else {
            startSpeechToText();
        }
    };

    const handleSubmit = async () => {
        setError(null);
        setBotAnswer('');

        if (!userAnswer.trim()) {
            setError("Please record a question first.");
            return;
        }

        try {
            const response = await fetch('http://localhost:5000/api/process_question', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: userAnswer }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                setError(errorData.error || 'Error processing question');
                return;
            }

            const data = await response.json();
            setBotAnswer(data.answer);
        } catch (error) {
            setError("Error processing the question. Please try again.");
        }
    };

    return (
        <div className="App">
            <h1>Vocal-Ed: One Stop Learning</h1>
            <button onClick={handleRecordButtonClick}>
                {isRecording ? "Stop Recording" : "Record Question"}
            </button>
            {userAnswer && <p>Recognized Text: {userAnswer}</p>}
            <button onClick={handleSubmit} disabled={!userAnswer || isRecording}>Get Answer</button>
            {botAnswer && <p>Database Answer: {botAnswer}</p>}
            {error && <p style={{ color: 'red' }}>{error}</p>}
            {speechError && <p style={{ color: 'red' }}>Speech Error: {speechError}</p>}
        </div>
    );
}

export default App;
