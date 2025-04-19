import { useState } from 'react';
import PromptBox from './components/PromptBox';

function App() {
  const [response, setResponse] = useState('');

  const handlePrompt = async (prompt) => {
    const res = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt }),
    });

    const data = await res.json();
    setResponse(data.response);
  };

  return (
    <div style={{ maxWidth: '600px', margin: 'auto', padding: '2rem' }}>
      <h1 style={{ marginBottom: '1rem' }}>LLaMA Chat</h1>
      <PromptBox onSubmit={handlePrompt} />
      {response && (
        <div style={{ marginTop: '2rem', padding: '1rem', background: '#f0f0f0', borderRadius: '0.5rem' }}>
          <strong>Response:</strong>
          <p>{response}</p>
        </div>
      )}
    </div>
  );
}

export default App;