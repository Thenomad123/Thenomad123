README.md

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
  return response.data.filter(event => event.type === 'PushEvent').map(event 

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
// src/api/githubAPI.js
import axios from 'axios';

// Prosty mechanizm cache w pamięci
const cache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minut

function getCache(key) {
  const cached = cache.get(key);
  if (cached && (Date.now() - cached.timestamp < CACHE_DURATION)) {
    return cached.data;
  }
  cache.delete(key);
  return null;
}

function setCache(key, data) {
  cache.set(key, { data, timestamp: Date.now() });
}

// Funkcja pobierająca dane z GitHub API z obsługą cache i mechanizmem retry w przypadku błędów
export async function fetchFromGitHub(url, config = {}) {
  const cacheKey = url;
  const cachedData = getCache(cacheKey);
  if (cachedData) {
    return cachedData;
  }
  
  try {
    const response = await axios.get(url, config);
    setCache(cacheKey, response.data);
    return response.data;
  } catch (error) {
    // Obsługa błędu – można dodać retry lub logikę powiadamiania
    throw error;
  }
}
// src/features/github/githubSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { fetchFromGitHub } from '../../api/githubAPI';

const GITHUB_USERNAME = 'twoj-github-login'; // Uzupełnij swoim loginem
const GITHUB_TOKEN = process.env.REACT_APP_GITHUB_TOKEN;

// Konfiguracja zapytań z nagłówkiem autoryzacji
const axiosConfig = {
  headers: {
    Authorization: `token ${GITHUB_TOKEN}`
  }
};

/**
 * Thunk pobierający zdarzenia typu PushEvent
 */
export const fetchGitHubData = createAsyncThunk(
  'github/fetchGitHubData',
  async (_, { rejectWithValue }) => {
    const url = `https://api.github.com/users/${GITHUB_USERNAME}/events`;
    try {
      const data = await fetchFromGitHub(url, axiosConfig);
      // Filtrujemy zdarzenia PushEvent i mapujemy do wymaganej struktury
      const pushEvents = data
        .filter(event => event.type === 'PushEvent')
        .map(event => ({
          repo: event.repo.name,
          message: event.payload.commits.map(commit => commit.message).join('; ')
        }));
      return pushEvents;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

/**
 * Thunk pobierający dane dla GitHub Copilot
 * Uwaga: API Copilota nie jest publiczne, więc poniższy kod symuluje pobieranie danych.
 */
export const fetchCopilotData = createAsyncThunk(
  'github/fetchCopilotData',
  async (_, { rejectWithValue }) => {
    // Fikcyjny endpoint – należy dostosować, gdyby API było dostępne
    const url = `https://api.github.com/copilot/data`;
    try {
      const data = await fetchFromGitHub(url, axiosConfig);
      // Przykładowa walidacja otrzymanych danych
      if (!data || typeof data !== 'object') {
        throw new Error('Nieprawidłowa struktura danych dla Copilot');
      }
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

/**
 * Thunk pobierający issues dla danego repozytorium
 */
export const fetchIssues = createAsyncThunk(
  'github/fetchIssues',
  async (repoName, { rejectWithValue }) => {
    const url = `https://api.github.com/repos/${repoName}/issues`;
    try {
      const data = await fetchFromGitHub(url, axiosConfig);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

const githubSlice = createSlice({
  name: 'github',
  initialState: {
    pushEvents: [],
    copilotData: null,
    issues: {},
    loading: false,
    error: null
  },
  reducers: {},
  extraReducers: builder => {
    // Obsługa fetchGitHubData
    builder
      .addCase(fetchGitHubData.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchGitHubData.fulfilled, (state, action) => {
        state.loading = false;
        state.pushEvents = action.payload;
      })
      .addCase(fetchGitHubData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Obsługa fetchCopilotData
      .addCase(fetchCopilotData.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCopilotData.fulfilled, (state, action) => {
        state.loading = false;
        state.copilotData = action.payload;
      })
      .addCase(fetchCopilotData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Obsługa fetchIssues
      .addCase(fetchIssues.pending, state => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchIssues.fulfilled, (state, action) => {
        state.loading = false;
        // Przechowujemy issues z kluczem repozytorium
        state.issues[action.meta.arg] = action.payload;
      })
      .addCase(fetchIssues.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});

export default githubSlice.reducer;
// src/tests/githubSlice.test.js
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import reducer, { fetchGitHubData, fetchCopilotData, fetchIssues } from '../features/github/githubSlice';
import * as githubAPI from '../api/githubAPI';

const middlewares = [thunk];
const mockStore = configureStore(middlewares);

// Mockowanie modułu API
jest.mock('../api/githubAPI');

describe('GitHub Slice', () => {
  let store;

  beforeEach(() => {
    store = mockStore({
      pushEvents: [],
      copilotData: null,
      issues: {},
      loading: false,
      error: null
    });
  });

  it('poprawnie pobiera zdarzenia push', async () => {
    const mockData = [
      {
        type: 'PushEvent',
        repo: { name: 'repo1' },
        payload: { commits: [{ message: 'Initial commit' }] }
      }
    ];
    githubAPI.fetchFromGitHub.mockResolvedValue(mockData);

    await store.dispatch(fetchGitHubData());
    const actions = store.getActions();
    expect(actions[0].type).toBe(fetchGitHubData.pending.type);
    expect(actions[1].type).toBe(fetchGitHubData.fulfilled.type);
    expect(actions[1].payload).toEqual([{ repo: 'repo1', message: 'Initial commit' }]);
  });

  it('obsługuje błąd przy pobieraniu zdarzeń push', async () => {
    const errorMessage = 'Network Error';
    githubAPI.fetchFromGitHub.mockRejectedValue(new Error(errorMessage));

    await store.dispatch(fetchGitHubData());
    const actions = store.getActions();
    expect(actions[0].type).toBe(fetchGitHubData.pending.type);
    expect(actions[1].type).toBe(fetchGitHubData.rejected.type);
    expect(actions[1].payload).toBe(errorMessage);
  });

  // Analogiczne testy można napisać dla fetchCopilotData oraz fetchIssues
});
// src/App.js
import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchGitHubData, fetchCopilotData, fetchIssues } from './features/github/githubSlice';

function App() {
  const dispatch = useDispatch();
  const { pushEvents, copilotData, issues, loading, error } = useSelector(state => state.github);

  useEffect(() => {
    dispatch(fetchGitHubData());
    dispatch(fetchCopilotData());
    // Przykładowo, można pobrać issues dla konkretnego repozytorium
    // dispatch(fetchIssues('repo1'));
  }, [dispatch]);

  return (
    <div className="App">
      <h1>Aktywność GitHub</h1>
      {loading && <p>Ładowanie...</p>}
      {error && <p>Błąd: {error}</p>}
      
      <section>
        <h2>Zdarzenia Push</h2>
        {pushEvents.length > 0 ? (
          <ul>
            {pushEvents.map((event, index) => (
              <li key={index}>
                Repo: {event.repo} – Wiadomość: {event.message}
              </li>
            ))}
          </ul>
        ) : (
          <p>Brak danych.</p>
        )}
      </section>

      <section>
        <h2>Dane Copilot</h2>
        {copilotData ? (
          <pre>{JSON.stringify(copilotData, null, 2)}</pre>
        ) : (
          <p>Brak danych Copilot.</p>
        )}
      </section>

      <section>
        <h2>Issues</h2>
        {Object.keys(issues).length > 0 ? (
          Object.entries(issues).map(([repo, issuesList]) => (
            <div key={repo}>
              <h3>Repozytorium: {repo}</h3>
              <ul>
                {issuesList.map(issue => (
                  <li key={issue.id}>{issue.title}</li>
                ))}
              </ul>
            </div>
          ))
        ) : (
          <p>Brak issues.</p>
        )}
      </section>
    </div>
  );
}

export default App;
// src/index.js
import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import githubReducer from './features/github/githubSlice';
import App from './App';

const store = configureStore({
  reducer: {
    github: githubReducer
  }
});

ReactDOM.render(
  <Provider store={store}>
    <App />
  </Provider>,
  document.getElementById('root')
);
// src/api/githubAPI.js
import axios from 'axios';

// Prosty mechanizm cache w pamięci
const cache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minut

function getCache(key) {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data;
  }
  cache.delete(key);
  return null;
}

function setCache(key, data) {
  cache.set(key, { data, timestamp: Date.now() });
}

// Funkcja pobierająca dane z GitHub API z obsługą cache i mechanizmem retry w przypadku błędów
export async function fetchFromGitHub(url, config = {}) {
  const cacheKey = url;
  const cachedData = getCache(cacheKey);
  if (cachedData) {
    return cachedData;
  }
  
  try {
    const response = await axios.get(url, config);
    setCache(cacheKey, response.data);
    return response.data;
  } catch (error) {
    // Obsługa błędu – można dodać retry lub logikę powiadamiania
    throw error;
  }
}
// src/App.js
import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchGitHubData, fetchCopilotData, fetchIssues } from './features/github/githubSlice';

function App() {
  const dispatch = useDispatch();
  const { pushEvents, copilotData, issues, loading, error } = useSelector(state => state.github);

  useEffect(() => {
    dispatch(fetchGitHubData());
    dispatch(fetchCopilotData());
    // Przykładowo, można pobrać issues dla konkretnego repozytorium:
    // dispatch(fetchIssues('repo1'));
  }, [dispatch]);

  return (
    <div className="App">
      <h1>Aktywność GitHub</h1>
      {loading && <p>Ładowanie...</p>}
      {error && <p>Błąd: {error}</p>}
      
      <section>
        <h2>Zdarzenia Push</h2>
        {pushEvents.length > 0 ? (
          <ul>
            {pushEvents.map((event, index) => (
              <li key={index}>
                Repo: {event.repo} – Wiadomość: {event.message}
              </li>
            ))}
          </ul>
        ) : (
          <p>Brak danych.</p>
        )}
      </section>

      <section>
        <h2>Dane Copilot</h2>
        {copilotData ? (
          <pre>{JSON.stringify(copilotData, null, 2)}</pre>
        ) : (
          <p>Brak danych Copilot.</p>
        )}
      </section>

      <section>
        <h2>Issues</h2>
        {Object.keys(issues).length > 0 ? (
          Object.entries(issues).map(([repo, issuesList]) => (
            <div key={repo}>
              <h3>Repozytorium: {repo}</h3>
              <ul>
                {issuesList.map(issue => (
                  <li key={issue.id}>{issue.title}</li>
                ))}
              </ul>
            </div>
          ))
        ) : (
          <p>Brak issues.</p>
        )}
      </section>
    </div>
  );
}

export default App;// src/api/githubAPI.js
import axios from 'axios';

// Prosty mechanizm cache w pamięci
const cache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minut

function getCache(key) {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data;
  }
  cache.delete(key);
  return null;
}

function setCache(key, data) {
  cache.set(key, { data, timestamp: Date.now() });
}

// Funkcja pobierająca dane z GitHub API z obsługą cache i mechanizmem retry w przypadku błędów
export async function fetchFromGitHub(url, config = {}) {
  const cacheKey = url;
  const cachedData = getCache(cacheKey);
  if (cachedData) {
    return cachedData;
  }
  
  try {
    const response = await axios.get(url, config);
    setCache(cacheKey, response.data);
    return response.data;
  } catch (error) {
    // Obsługa błędu – można dodać retry lub logikę powiadamiania
    throw error;
  }
}