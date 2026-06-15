'use client';
import { useState, useCallback, useRef, useEffect } from 'react';
import { supabase } from '../../lib/supabaseClient';
import { useSpeech } from '../../lib/useSpeech';

export default function ChatAssistant() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [userLanguage, setUserLanguage] = useState('English');
  const [session, setSession] = useState(null);
  const [initializing, setInitializing] = useState(true);
  const [missingField, setMissingField] = useState(null);
  const { speak, listen, isListening } = useSpeech();
  const messagesEndRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const fetchInitialQuestion = useCallback(async (token) => {
    setLoading(true);
    try {
      const res = await fetch('/api/backend/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({})
      });
      const data = await res.json();
      if (data.question) {
        setMessages([{ role: 'assistant', content: data.question }]);
        setMissingField(data.missing_field);
        speak(data.question, userLanguage);
      }
    } catch (error) {
      console.error("Failed to fetch initial question", error);
    } finally {
      setLoading(false);
    }
  }, [speak, userLanguage]);

  useEffect(() => {
    let mounted = true;

    const initSession = async () => {
        const { data: { session: currentSession } } = await supabase.auth.getSession();
        if (mounted) {
            setSession(currentSession);
            setInitializing(false);
            if (currentSession) {
                fetchInitialQuestion(currentSession.access_token);
            }
        }
    };

    initSession();

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, currentSession) => {
      if (mounted) {
        setSession(currentSession);
      }
    });

    return () => {
        mounted = false;
        if (subscription && subscription.unsubscribe) {
            subscription.unsubscribe();
        }
    };
  }, [fetchInitialQuestion]);

  const sendMessage = useCallback(async (text) => {
    const messageToSend = text || inputText;
    if (!messageToSend.trim() || !session) return;

    const userMessage = { role: 'user', content: messageToSend };
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setLoading(true);
    setMissingField(null); // Clear buttons while loading

    try {
      const res = await fetch('/api/backend/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({ message: messageToSend })
      });
      
      if (!res.ok) {
        const errorText = await res.text();
        console.error("Backend returned error:", res.status, errorText);
        throw new Error(`Server error: ${res.status}`);
      }
      
      const data = await res.json();
      
      if (data.question) {
        setMessages(prev => [...prev, { role: 'assistant', content: data.question }]);
        setMissingField(data.missing_field);
        
        let currentLang = userLanguage;
        if (data.profile?.preferred_language) {
            setUserLanguage(data.profile.preferred_language);
            currentLang = data.profile.preferred_language;
        }

        speak(data.question, currentLang);
      }
    } catch (error) {
      console.error("Detailed Fetch Error:", error);
      setMessages(prev => [...prev, { role: 'assistant', content: `Sorry, I'm having trouble connecting to the server.` }]);
    } finally {
      setLoading(false);
    }
  }, [inputText, session, speak, userLanguage]);

  const handleVoiceInput = useCallback(() => {
    listen((transcript) => {
      sendMessage(transcript);
    }, userLanguage);
  }, [listen, sendMessage, userLanguage]);

  if (initializing) {
    return (
        <div className="flex flex-col h-[600px] bg-white rounded-xl shadow-xl border items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-2"></div>
            <p className="text-gray-500 text-sm">Initializing assistant...</p>
        </div>
    );
  }

  if (!session) {
    return (
        <div className="flex flex-col h-[600px] bg-white rounded-xl shadow-xl border items-center justify-center p-8 text-center">
            <p className="text-gray-500 mb-4">Please log in to talk with the AI assistant.</p>
        </div>
    );
  }

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-xl shadow-xl border overflow-hidden">
      <main className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] p-3 rounded-2xl shadow-sm ${
              msg.role === 'user' 
                ? 'bg-blue-600 text-white rounded-tr-none' 
                : 'bg-white text-gray-800 border rounded-tl-none'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border p-3 rounded-2xl shadow-sm animate-pulse">
              Typing...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>

      {/* Suggestions / Buttons */}
      {!loading && missingField === 'sector' && (
        <div className="px-4 py-2 bg-gray-50 flex gap-2 overflow-x-auto border-t">
          {['Farmer', 'Student', 'Women'].map(opt => (
            <button
              key={opt}
              onClick={() => sendMessage(opt)}
              className="bg-white border-2 border-blue-600 text-blue-600 px-4 py-1 rounded-full text-sm font-medium hover:bg-blue-600 hover:text-white transition-all whitespace-nowrap"
            >
              {opt}
            </button>
          ))}
        </div>
      )}

      {/* Input Area */}
      <footer className="p-4 border-t bg-white">
        <div className="flex gap-2 bg-gray-100 p-1 rounded-full px-4 items-center">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Type your message..."
            className="flex-1 bg-transparent py-2 focus:outline-none text-sm text-gray-800"
          />
          
          <button
            onClick={handleVoiceInput}
            className={`p-2 rounded-full transition-all ${
              isListening ? 'bg-red-500 text-white scale-110' : 'text-gray-500 hover:text-blue-600'
            }`}
          >
            {isListening ? 'listening' : 'mic'}
          </button>

          <button
            onClick={() => sendMessage()}
            disabled={loading || !inputText.trim()}
            className="text-blue-600 font-semibold text-sm disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </footer>
    </div>
  );
}
