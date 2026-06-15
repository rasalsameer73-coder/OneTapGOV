'use client';
import { useState, useCallback, useRef, useEffect } from 'react';
import { supabase } from '@/lib/supabaseClient';
import { useSpeech } from '@/lib/useSpeech';

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [userLanguage, setUserLanguage] = useState('English');
  const [session, setSession] = useState(null);
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
        speak(data.question, userLanguage);
      }
    } catch (error) {
      console.error("Failed to fetch initial question", error);
    } finally {
      setLoading(false);
    }
  }, [speak, userLanguage]);

  useEffect(() => {
    // Get session on mount
    supabase.auth.getSession().then(({ data: { session: currentSession } }) => {
      setSession(currentSession);
      if (currentSession) fetchInitialQuestion(currentSession.access_token);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, currentSession) => {
      setSession(currentSession);
    });

    return () => {
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

    try {
      const res = await fetch('/api/backend/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({ message: messageToSend })
      });
      
      const data = await res.json();
      
      if (data.question) {
        setMessages(prev => [...prev, { role: 'assistant', content: data.question }]);
        
        if (data.profile?.preferred_language) {
            setUserLanguage(data.profile.preferred_language);
        }

        speak(data.question, data.profile?.preferred_language || userLanguage);
      }
    } catch (error) {
      console.error("Error sending message", error);
      setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I'm having trouble connecting to the server." }]);
    } finally {
      setLoading(false);
    }
  }, [inputText, session, speak, userLanguage]);

  const handleVoiceInput = useCallback(() => {
    listen((transcript) => {
      sendMessage(transcript);
    }, userLanguage);
  }, [listen, sendMessage, userLanguage]);

  if (!session) {
    return <div className="p-8 text-center">Please log in to use the chat.</div>;
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b p-4 shadow-sm">
        <h1 className="text-xl font-bold text-blue-600">OneTapGov Assistant</h1>
      </header>

      {/* Chat Messages */}
      <main className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-lg shadow-sm ${
              msg.role === 'user' 
                ? 'bg-blue-600 text-white rounded-br-none' 
                : 'bg-white text-gray-800 border rounded-bl-none'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border p-3 rounded-lg shadow-sm animate-pulse">
              Typing...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>

      {/* Input Area */}
      <footer className="bg-white border-t p-4">
        <div className="max-w-4xl mx-auto flex gap-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Type your message..."
            className="flex-1 border rounded-full px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          
          <button
            onClick={handleVoiceInput}
            className={`p-3 rounded-full transition-colors ${
              isListening ? 'bg-red-500 animate-pulse' : 'bg-gray-100 hover:bg-gray-200'
            }`}
            title="Speak"
          >
            {isListening ? '🛑' : '🎤'}
          </button>

          <button
            onClick={() => sendMessage()}
            disabled={loading || !inputText.trim()}
            className="bg-blue-600 text-white px-6 py-2 rounded-full hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            Send
          </button>
        </div>
      </footer>
    </div>
  );
}
