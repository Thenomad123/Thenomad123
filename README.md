I😁- 👋 Hi, I’m @Thenomad123
- 👀 I’m interested in ...
- 🌱 I’m currently learning ...
- 💞️ I’m looking to collaborate on ...
- 📫 How to reach me ...
- 😄 Pronouns: ...
- ⚡ Fun fact: ...

<!---
Thenomad123/Thenomad123 is a ✨ special ✨ repository because its `README.md` (this file) appears on your GitHub profile.
You can click the Preview link to take a look at your changes.
--->
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Pobieranie aktywności GitHub
export const fetchGitHubData = createAsyncThunk('chatbot/fetchGitHub', async (username) => {
  const response = await axios.get(`https://api.github.com/users/${username}/events`, {
    headers: { Authorization: `Bearer ${process.env.REACT_APP_GITHUB_TOKEN}` }
  });
  return response.data.filter(event => event.type === 'PushEvent').map(event => ({
    repo: event.repo.name,
    message: event.payload.commits?.[0]?.message || 'Brak opisu'
  }));
});

// Pobieranie odpowiedzi z Copilot
export const fetchCopilotData = createAsyncThunk('chatbot/fetchCopilot', async (prompt) => {
  const response = await axios.post('https://api.copilot.microsoft.com/v1/completions', {
    prompt,
    max_tokens: 150
  }, {
    headers: { 
      Authorization: `Bearer ${process.env.REACT_APP_COPILOT_TOKEN}`,
      'Content-Type': 'application/json'
    }
  });
  return response.data.choices[0].text;
});

const chatbotSlice = createSlice({
  name: 'chatbot',
  initialState: { 
    githubData: [], copilotData: '', 
    clipboard: '', notes: [], files: [], 
    status: 'idle', error: null 
  },
  reducers: {
    addNote: (state, action) => { state.notes.push(action.payload); },
    deleteNote: (state, action) => { state.notes = state.notes.filter(n => n.id !== action.payload); },
    setClipboard: (state, action) => { state.clipboard = action.payload; },
    saveFile: (state, action) => { state.files.push(action.payload); }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchGitHubData.fulfilled, (state, action) => { state.githubData = action.payload; })
      .addCase(fetchCopilotData.fulfilled, (state, action) => { state.copilotData = action.payload; });
  }
});

export const { addNote, deleteNote, setClipboard, saveFile } = chatbotSlice.actions;
export default chatbotSlice.reducer;export const startSpeechRecognition = (onResult, onEnd) => {
  const recognition = new window.SpeechRecognition();
  recognition.lang = 'pl-PL';
  recognition.continuous = false;
  recognition.interimResults = false;
  
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    onResult(transcript);
  };
  
  recognition.onerror = (event) => {
    console.error("Błąd rozpoznawania mowy:", event.error);
  };

  recognition.onend = () => {
    if (onEnd) onEnd();
  };

  recognition.start();
};

export const speakText = (text) => {
  const synth = window.speechSynthesis;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'pl-PL';
  synth.speak(utterance);
};export const startSpeechRecognition = (onResult, onEnd) => {
  const recognition = new window.SpeechRecognition();
  recognition.lang = 'pl-PL';
  recognition.continuous = false;
  recognition.interimResults = false;
  
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    onResult(transcript);
  };
  
  recognition.onerror = (event) => {
    console.error("Błąd rozpoznawania mowy:", event.error);
  };

  recognition.onend = () => {
    if (onEnd) onEnd();
  };

  recognition.start();
};

export const speakText = (text) => {
  const synth = window.speechSynthesis;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'pl-PL';
  synth.speak(utterance);
};import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Input, Button, List, Typography } from 'antd';
import { AudioOutlined, SendOutlined } from '@ant-design/icons';
import { fetchCopilotData } from '../features/chatbotSlice';
import { startSpeechRecognition, speakText } from '../utils/speech';

const { TextArea } = Input;
const { Title } = Typography;

const Chatbot = () => {
  const [message, setMessage] = useState('');
  const dispatch = useDispatch();
  const { copilotData } = useSelector(state => state.chatbot);

  const handleSend = () => {
    if (message.trim()) {
      dispatch(fetchCopilotData(message));
      setMessage('');
    }
  };

  const handleVoiceInput = () => {
    startSpeechRecognition((transcript) => {
      setMessage(transcript);
      dispatch(fetchCopilotData(transcript));
    });
  };

  return (
    <div style={{ maxWidth: 600, margin: 'auto', padding: 24, background: '#f9f9f9', borderRadius: 8 }}>
      <Title level={3}>🤖 Chatbot AI</Title>
      <TextArea 
        rows={4} 
        value={message} 
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Wpisz wiadomość lub użyj mikrofonu..."
        style={{ marginBottom: 12 }}
      />
      <Button type="primary" icon={<SendOutlined />} onClick={handleSend} style={{ marginRight: 8 }}>
        Wyślij
      </Button>
      <Button type="default" icon={<AudioOutlined />} onClick={handleVoiceInput}>
        Mów
      </Button>

      {copilotData && (
        <List
          style={{ marginTop: 24, background: '#fff', padding: 12, borderRadius: 8 }}
          bordered
          dataSource={[{ text: copilotData }]}
          renderItem={item => (
            <List.Item onClick={() => speakText(item.text)}>
              <Typography.Text>{item.text}</Typography.Text>
            </List.Item>
          )}
        />
      )}
    </div>
  );
};

export default Chatbot;import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

export const fetchCopilotData = createAsyncThunk('chatbot/fetchCopilot', async (prompt, { getState }) => {
  const { modelSettings } = getState().chatbot;
  const response = await axios.post('https://api.copilot.microsoft.com/v1/completions', {
    prompt,
    max_tokens: modelSettings.maxTokens || 150
  }, {
    headers: { 
      Authorization: `Bearer ${process.env.REACT_APP_COPILOT_TOKEN}`,
      'Content-Type': 'application/json'
    }
  });
  return { prompt, response: response.data.choices[0].text };
});

const chatbotSlice = createSlice({
  name: 'chatbot',
  initialState: { 
    chatHistory: [], notes: [], files: [], clipboard: '', 
    copilotData: '', modelSettings: { maxTokens: 150 }, 
    status: 'idle', error: null 
  },
  reducers: {
    addMessage: (state, action) => {
      state.chatHistory.push(action.payload);
    },
    clearHistory: (state) => {
      state.chatHistory = [];
    },
    addNote: (state, action) => {
      state.notes.push(action.payload);
    },
    deleteNote: (state, action) => {
      state.notes = state.notes.filter(n => n.id !== action.payload);
    },
    saveFile: (state, action) => {
      state.files.push(action.payload);
    },
    setModelSettings: (state, action) => {
      state.modelSettings = { ...state.modelSettings, ...action.payload };
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCopilotData.fulfilled, (state, action) => {
        state.chatHistory.push({ role: 'assistant', text: action.payload.response });
        state.copilotData = action.payload.response;
      });
  }
});

export const { addMessage, clearHistory, addNote, deleteNote, saveFile, setModelSettings } = chatbotSlice.actions;
export default chatbotSlice.reducer;import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Input, Button, List, Typography, Select, Modal } from 'antd';
import { AudioOutlined, SendOutlined, SaveOutlined, DeleteOutlined } from '@ant-design/icons';
import { fetchCopilotData, addMessage, clearHistory, setModelSettings } from '../features/chatbotSlice';
import { startSpeechRecognition, speakText } from '../utils/speech';

const { TextArea } = Input;
const { Title } = Typography;
const { Option } = Select;

const Chatbot = () => {
  const [message, setMessage] = useState('');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const dispatch = useDispatch();
  const { chatHistory, modelSettings } = useSelector(state => state.chatbot);

  const handleSend = () => {
    if (message.trim()) {
      dispatch(addMessage({ role: 'user', text: message }));
      dispatch(fetchCopilotData(message));
      setMessage('');
    }
  };

  const handleVoiceInput = () => {
    startSpeechRecognition((transcript) => {
      setMessage(transcript);
      dispatch(addMessage({ role: 'user', text: transcript }));
      dispatch(fetchCopilotData(transcript));
    });
  };

  const handleSaveHistory = () => {
    const blob = new Blob([JSON.stringify(chatHistory, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat_history_${new Date().toISOString()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div style={{ maxWidth: 600, margin: 'auto', padding: 24, background: '#f9f9f9', borderRadius: 8 }}>
      <Title level={3}>🤖 Chatbot AI</Title>

      <Select 
        defaultValue={modelSettings.maxTokens} 
        onChange={(value) => dispatch(setModelSettings({ maxTokens: value }))}
        style={{ width: '100%', marginBottom: 16 }}
      >
        <Option value={50}>Bardzo krótka odpowiedź</Option>
        <Option value={150}>Standardowa odpowiedź</Option>
        <Option value={300}>Dłuższa odpowiedź</Option>
      </Select>

      <TextArea 
        rows={4} 
        value={message} 
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Wpisz wiadomość lub użyj mikrofonu..."
        style={{ marginBottom: 12 }}
      />
      
      <Button type="primary" icon={<SendOutlined />} onClick={handleSend} style={{ marginRight: 8 }}>
        Wyślij
      </Button>
      <Button type="default" icon={<AudioOutlined />} onClick={handleVoiceInput} style={{ marginRight: 8 }}>
        Mów
      </Button>
      <Button type="dashed" icon={<SaveOutlined />} onClick={handleSaveHistory}>
        Zapisz historię
      </Button>

      <List
        style={{ marginTop: 24, background: '#fff', padding: 12, borderRadius: 8 }}
        bordered
        dataSource={chatHistory}
        renderItem={item => (
          <List.Item 
            style={{ background: item.role === 'user' ? '#e6f7ff' : '#f6ffed' }} 
            onClick={() => speakText(item.text)}
          >
            <Typography.Text>{item.text}</Typography.Text>
          </List.Item>
        )}
      />

      {chatHistory.length > 0 && (
        <Button 
          danger 
          icon={<DeleteOutlined />} 
          style={{ marginTop: 16 }} 
          onClick={() => dispatch(clearHistory())}
        >
          Wyczyść historię
        </Button>
      )}

      <Modal
        title="Ustawienia Modelu AI"
        open={isSettingsOpen}
        onCancel={() => setIsSettingsOpen(false)}
        footer={null}
      >
        <p>Wybierz maksymalną liczbę tokenów dla odpowiedzi AI.</p>
      </Modal>
    </div>
  );
};

export default Chatbot;### Uwagi i Sugestie:
1. **Obsługa błędów**  
   - Brakuje obsługi błędów dla `fetchCopilotData`. Możesz dodać stan `error` do Copilot API, aby informować użytkownika, gdy coś pójdzie nie tak.
   - Dodaj obsługę przypadków, gdy `event.payload.commits` jest pusty.

2. **Poprawki UI**  
   - `Input.TextArea` dla `clipboardContent` mógłby mieć `autoSize` dla lepszego UX.
   - Możesz dodać `message.success()` z `antd`, gdy użytkownik skopiuje tekst do schowka.

3. **Wydajność**  
   - `handleFetchGitHub` i `handleCopilotRequest` nie sprawdzają, czy dany request już trwa. Można dodać `useCallback`, by uniknąć niepotrzebnych renderów.

Czy planujesz dodać więcej funkcjonalności do tej aplikacji? Może np. historię zapytań AI?