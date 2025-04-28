import { useState } from 'react';

export default function PromptBox({ onSubmit }) {
  const [prompt, setPrompt] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    onSubmit(prompt);
    setPrompt('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        rows="4"
        placeholder="Type your prompt here..."
        style={{ width: '100%', padding: '1rem', borderRadius: '0.5rem' }}
      />
      <button type="submit" style={{ marginTop: '1rem' }}>
        Submit
      </button>
    </form>
  );
}