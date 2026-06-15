'use client';
import { useState, useCallback, useRef } from 'react';

export const useSpeech = () => {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  // 1. Text to Speech (AI speaks)
  const speak = useCallback((text, language = 'English') => {
    if (typeof window === 'undefined') return;

    // Stop any current speech
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Map language names to BCP 47 tags
    const langMap = {
      "English": "en-IN",
      "Hindi": "hi-IN",
      "Marathi": "mr-IN",
      "Bengali": "bn-IN",
      "Tamil": "ta-IN",
      "Telugu": "te-IN",
      "Kannada": "kn-IN",
      "Gujarati": "gu-IN"
    };
    
    utterance.lang = langMap[language] || "en-IN";
    window.speechSynthesis.speak(utterance);
  }, []);

  // 2. Speech to Text (User speaks)
  const listen = useCallback((onResult, language = 'English') => {
    if (typeof window === 'undefined') return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Your browser does not support speech recognition.");
      return;
    }

    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }

    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;
    
    recognition.continuous = false;
    recognition.interimResults = false;
    
    // Set recognition language based on preference
    const langMap = {
      "English": "en-IN",
      "Hindi": "hi-IN",
      "Marathi": "mr-IN"
    };
    recognition.lang = langMap[language] || "en-IN";
    
    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = (event) => {
      console.error("Speech recognition error", event.error);
      setIsListening(false);
    };
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      onResult(transcript);
    };

    recognition.start();
  }, []);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  }, []);

  return { speak, listen, stopListening, isListening };
};
