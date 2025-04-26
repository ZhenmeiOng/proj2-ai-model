import { useState } from 'react';
import PromptBox from './components/PromptBox';

function App() {
  // const [response, setResponse] = useState('');
  const [prompt, setPrompt] = useState('');
  const [jobId, setJobId] = useState('');
  const [status, setStatus] = useState('');

  // const handlePrompt = async (prompt) => {
  //   const res = await fetch('http://localhost:8000/api/chat', {
  //     method: 'POST',
  //     headers: { 'Content-Type': 'application/json' },
  //     body: JSON.stringify({ prompt }),
  //   });

  //   const data = await res.json();
  //   setResponse(data.response);
  // };

  async function submitJob() {
    // const prompt = document.getElementById("prompt").value;

    if (!prompt.trim()) {
      alert("Please enter a prompt!");
      return;
    }

    // Build the job script (simple template)
    const script = `#!/bin/bash
#SBATCH --job-name=deepseek_test    # Job name
#SBATCH --output=dp%j.out    # Standard output file
#SBATCH --error=dp%j.err     # Error file
#SBATCH --partition=ice-gpu         # Partition name (check with 'sinfo' if needed)
#SBATCH -N1 --gres=gpu:1       # Request 1 GPU
#SBATCH --cpus-per-task=4           # Request 4 CPU cores
#SBATCH --mem=32G                   # Request 16GB RAM
#SBATCH --time=01:00:00             # Max job runtime (hh:mm:ss)
#SBATCH --mail-type=END,FAIL        # Email notification (optional)
#SBATCH --mail-user=ychauhan9@gatech.edu  # Replace with your email

# Load necessary modules (modify as per your HPC environment)
module load anaconda3  # If Conda is available
source activate my_env  # Activate your Conda environment

export HUGGINGFACE_TOKEN=$(cat /home/hice1/ychauhan9/scratch/hgtoken.env)

# Run the DeepSeek Python script
python seek_test.py`;

    const response = await fetch("http://localhost:8000/jobs", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ script: script })
    });

    const data = await response.json();

    if (response.ok) {
      // these lines below only works for vanilla JS
      // currentJobId = data.job_id;
      // document.getElementById("job-status").style.display = "block";
      // document.getElementById("check-status-button").style.display = "block";
      // document.getElementById("job-status").innerText = `Job submitted! ID: ${currentJobId}`;
      
      // update React Page:
      setJobId(data.job_id);    // store the job id
      setStatus(`Job submitted! ID: ${data.job_id}`); // show status
    } else {
      alert("Error submitting job: " + data.detail);
    }
  }

  async function checkStatus() {
    if (!jobId) {
      alert("No job ID to check!");
      return;
    }

    const response = await fetch(`http://localhost:8000/jobs/${jobId}`);
    const data = await response.json();

    if (response.ok) {
      // document.getElementById("job-status").innerText = `Job ${currentJobId} is currently: ${data.state}`;
      setStatus(`Job ${jobId} is currently: ${data.state}`);
    } else {
      alert("Error checking job: " + data.detail);
    }
  }

  //xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

  return (
    <div className="App">
    {/* <div style={{ maxWidth: '600px', margin: 'auto', padding: '2rem' }}> */}
      <h1 style={{ marginBottom: '1rem' }}>DeepSeek Chat</h1>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Enter your prompt..."
        rows={8}
        cols={60}
      />
      <br />
      <button onClick={submitJob}>Submit Job</button>
      {jobId && (
        <>
          <h3>{status}</h3>
          <button onClick={checkStatus}>Check Status</button>
        </>
      )}
    </div>
  );
}

export default App;