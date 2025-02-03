import React, { useState, useEffect } from 'react';
import useSpeechToText from 'react-hook-speech-to-text';

function App() {
    const [userAnswer, setUserAnswer] = useState('');
    const [botAnswer, setBotAnswer] = useState('');
    const [recordingText, setRecordingText] = useState("Record Answer");
    const [error, setError] = useState(null);

    const {
        interimResult,
        results,
        startSpeechToText,
        stopSpeechToText,
        isRecording, // Use the isRecording state from the hook
    } = useSpeechToText({
        continuous: true,
        useLegacyResults: false,
    });

    useEffect(() => {
        console.log("Results Array:", results);

        if (results.length > 0) {
            setUserAnswer(results.map((result) => result.transcript).join(' ')); // Added space between words
        }
    }, [results]);

    useEffect(() => {
        console.log("Interim Result:", interimResult);
    }, [interimResult]);

    useEffect(() => {
        console.log("Hook's isRecording:", isRecording);
        setRecordingText(isRecording ? "Stop Recording" : "Record Answer"); // Update button text
    }, [isRecording]);

    const handleSubmit = async () => {
        setError(null); // Clear previous errors
        setBotAnswer(""); // Clear previous answer

        if (!userAnswer) {
            setError("Please record a question first.");
            return;
        }

        try {
            const response = await fetch('http://localhost:5000/api/process_question', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: userAnswer }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                setError(errorData.error || 'Error processing question');
                throw new Error(errorData.error || 'Error processing question');
            }

            const data = await response.json();
            setBotAnswer(data.answer);
        } catch (error) {
            console.error('Error:', error);
            setError("Error processing the question. Please try again."); // Set error message
        }
    };

    return (
        <div className="App">
            <h1>Speech to Text Demo</h1>
            <button
                onClick={isRecording ? stopSpeechToText : startSpeechToText}
                disabled={isRecording} // Disable while recording
            >
                {recordingText}
            </button>
            <p>Recognized Text: {userAnswer}</p>
            <button onClick={handleSubmit} disabled={!userAnswer || isRecording}> {/* Disable if no question or recording */}
                Get Answer
            </button>
            <p>Bot's Answer: {botAnswer}</p>
            {error && <p style={{ color: 'red' }}>{error}</p>}
        </div>
    );
}

export default App;