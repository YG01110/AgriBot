import { useState, useEffect, useRef, memo } from 'react';
import { BeatLoader } from 'react-spinners';
import { ArrowUpCircleIcon, MicrophoneIcon } from '@heroicons/react/24/solid';
import { motion, AnimatePresence } from 'framer-motion';
import { io } from 'socket.io-client';

const socket = io('http://localhost:5000');

const languageOptions = [
  { label: 'English', value: 'en' },
  { label: 'Kannada', value: 'kn' },
  { label: 'Hindi', value: 'hi' },
  { label: 'Telugu', value: 'te' },
  { label: 'Malayalam', value: 'ml' },
  { label: 'Tamil', value: 'ta' },
  { label: 'Bengali', value: 'bn' },
  { label: 'Marathi', value: 'mr' },
  { label: 'Gujarati', value: 'gu' },
  { label: 'Punjabi', value: 'pa' },
  { label: 'Urdu', value: 'ur' }
];

const TransformedItems = [
  { label: 'Crop prices', value: 'What are current prices?' },
  { label: 'Weather', value: 'Weather forecast?' },
  { label: 'Diseases', value: 'Crop diseases?' },
  { label: 'Schemes', value: 'Government schemes?' }
];

const MessageBubble = memo(({ item }) => {
  const [visibleLines, setVisibleLines] = useState(0);
  const [isNewMessage, setIsNewMessage] = useState(true);

  useEffect(() => {
    if (!item.self) {
      const timer = setTimeout(() => setIsNewMessage(false), 3000);
      return () => clearTimeout(timer);
    }
  }, []);

  useEffect(() => {
    if (!item.self && item.type === 'text') {
      const lines = item.message.split('<br>');
      let index = 0;
      const interval = setInterval(() => {
        index++;
        setVisibleLines(index);
        if (index >= lines.length) clearInterval(interval);
      }, 600);
      return () => clearInterval(interval);
    } else {
      setVisibleLines(999);
    }
  }, [item]);

  if (!item) return null;

  if (item.type === 'images' && Array.isArray(item.message)) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-[85%] p-4 mb-4 rounded-2xl backdrop-blur-xl shadow-lg transition-all duration-300 mr-auto bg-white/40 border-transparent relative overflow-hidden"
      >
        {isNewMessage && <div className="animate-border-shine" />}
        <div className="flex gap-3">
          {item.message.map((img, i) => (
            <img
              key={i}
              src={img}
              className="w-36 h-36 rounded-xl object-cover border border-white/30 shadow-inner"
              alt="Agricultural reference"
            />
          ))}
        </div>
      </motion.div>
    );
  }

  const lines = item.message.split('<br>');

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`max-w-[85%] p-4 mb-4 rounded-2xl backdrop-blur-xl shadow-lg transition-all duration-300 ${
        item.self
          ? 'ml-auto bg-white/60 border border-white/30'
          : 'mr-auto bg-white/40 border-transparent relative overflow-hidden'
      }`}
    >
      {!item.self && isNewMessage && <div className="animate-border-shine" />}
      <div className="space-y-2 overflow-x-auto scrollbar-smooth">
        <AnimatePresence mode="wait">
          {!item.self ? (
            lines.slice(0, visibleLines).map((line, lineIndex) => (
              <motion.div
                key={lineIndex}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
                className="overflow-hidden"
              >
                {line.split('').map((char, charIndex) => (
                  <motion.span
                    key={charIndex}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{
                      delay: charIndex * 0.01,
                      duration: 0.05
                    }}
                    className="text-gray-800 text-base leading-6 font-medium animate-text-shine bg-[linear-gradient(110deg,#1e3a8a,30%,#1d4ed8,50%,#1e3a8a)] bg-[length:250%_100%] bg-clip-text text-transparent"
                  >
                    {char}
                  </motion.span>
                ))}
              </motion.div>
            ))
          ) : (
            <p className="text-gray-800 text-base leading-6 font-medium">
              {item.message.replace(/<br>/g, ' ')}
            </p>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
});

export default function App() {
  const [text, setText] = useState('');
  const [chatMessage, setChatMessage] = useState([{
    message: 'Welcome to FarmAssist 🌾<br>How can I help you today?',
    self: false,
    type: 'text'
  }]);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [isListening, setIsListening] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const bottomRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  useEffect(() => {
    const handleMessage = (data) => {
      setIsLoading(false);
      const newMessages = [];
      if (data.text) newMessages.push({ message: data.text.replace(/\n/g, '<br>'), self: false, type: 'text' });
      if (data.images?.length) newMessages.push({ message: data.images, self: false, type: 'images' });
      setChatMessage(prev => [...prev, ...newMessages]);
    };
    socket.on('recv_message', handleMessage);
    return () => socket.off('recv_message', handleMessage);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessage]);

  const handleMicClick = () => {
    if (isListening) {
      recognitionRef.current?.stop(); setIsListening(false); return;
    }
    recognitionRef.current = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognitionRef.current.lang = selectedLanguage;
    recognitionRef.current.interimResults = false;
    recognitionRef.current.maxAlternatives = 1;
    recognitionRef.current.onstart = () => setIsListening(true);
    recognitionRef.current.onerror = () => setIsListening(false);
    recognitionRef.current.onend = () => setIsListening(false);
    recognitionRef.current.onresult = (event) => setText(event.results[0][0].transcript);
    recognitionRef.current.start();
  };

  const socketEmit = () => {
    if (!text.trim()) return;
    setIsLoading(true);
    setChatMessage(prev => [...prev, { message: text, self: true, type: 'text' }]);
    socket.emit('message', { message: text, language: selectedLanguage });
    setText('');
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      <div 
        className="fixed pointer-events-none -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-gradient-radial from-blue-100/20 via-transparent to-transparent mix-bl-lighten"
        style={{
          left: `${mousePos.x}px`,
          top: `${mousePos.y}px`,
        }}
      />

      <div className="absolute inset-0 bg-gradient-to-tr from-red-500/50 via-yellow-300/40 via-blue-300/40 to-purple-500/50 z-0" />

      <nav className="fixed top-0 w-full py-4 px-6 z-50 bg-white/20 backdrop-blur-xl border-b border-white/10">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-gray-900">FarmAssist</h1>
          <select
            value={selectedLanguage}
            onChange={e => setSelectedLanguage(e.target.value)}
            className="bg-white/50 rounded-lg px-4 py-2 text-gray-800 border border-white/20 focus:ring-2 focus:ring-white/30 transition-all"
          >
            {languageOptions.map(opt => (
              <option key={opt.value} value={opt.value} className="bg-white text-gray-800">
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto pt-24 pb-28 px-6 relative z-10">
        <div className="space-y-4">
          <AnimatePresence>
            {chatMessage.map((item, idx) => <MessageBubble key={idx} item={item} />)}
          </AnimatePresence>
          <div ref={bottomRef} />
        </div>
      </main>

      <div className="fixed bottom-0 w-full py-4 px-6 z-50 bg-white/20 backdrop-blur-xl border-t border-white/10">
        <div className="max-w-7xl mx-auto flex items-center gap-3 relative">
          <div className="flex-1 relative">
            <input
              value={text}
              onChange={e => setText(e.target.value)}
              onKeyPress={e => e.key === 'Enter' && socketEmit()}
              placeholder="Ask about crops, weather, or prices..."
              className="w-full bg-white/50 rounded-2xl pl-6 pr-14 py-3.5 text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-white/30 border border-white/20 transition-all"
            />
            {text && (
              <div className="absolute bottom-full mb-3 w-full bg-white/70 backdrop-blur-lg rounded-xl shadow-2xl p-3 z-[999] max-h-48 overflow-y-auto">
                {TransformedItems.filter(itm => itm.label.toLowerCase().includes(text.toLowerCase())).map((itm, key) => (
                  <div
                    key={key}
                    onClick={() => setText(itm.value)}
                    className="p-3 hover:bg-white/40 rounded-lg cursor-pointer text-gray-800 text-sm transition-colors"
                  >{itm.label}</div>
                ))}
              </div>
            )}
            <button
              onClick={handleMicClick}
              className={`absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-full shadow-lg transition-all duration-300 ${isListening ? 'bg-red-400/50' : 'bg-white/50 hover:bg-white/70'}`}
            >
              <MicrophoneIcon className="w-6 h-6 text-gray-800" />
            </button>
          </div>
          <button
            onClick={socketEmit}
            disabled={isLoading}
            className="bg-white/50 hover:bg-white/70 p-3.5 rounded-full disabled:opacity-50 transition-all shadow-lg backdrop-blur-md hover:shadow-white/20"
          >
            <ArrowUpCircleIcon className="w-7 h-7 text-gray-800" />
          </button>
        </div>
      </div>

      {isLoading && (
        <div className="fixed inset-0 bg-black/10 flex items-center justify-center z-50">
          <div className="bg-white/20 backdrop-blur-lg p-6 rounded-2xl flex items-center space-x-3 border-2 border-white/20 shadow-2xl">
            <BeatLoader size={12} color="#60A5FA" />
            <span className="text-gray-800 font-semibold">Analyzing request...</span>
          </div>
        </div>
      )}
    </div>
  );
}