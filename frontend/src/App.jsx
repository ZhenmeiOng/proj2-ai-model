import { useState } from 'react';

function App() {
  const [prompt, setPrompt] = useState('');
  const [jobId, setJobId] = useState('');
  const [status, setStatus] = useState('');
  const [output, setOutput] = useState('');

  async function submitJob() {
    // const prompt = document.getElementById("prompt").value;

    if (!prompt.trim()) {
      alert("Please enter a prompt!");
      return;
    }

    const escapedPrompt = prompt.replace(/"/g, '\\"');

    const script = `#!/bin/bash
#SBATCH --job-name=deepseek_test    # Job name
#SBATCH --output=./scratch/p2-output/dp%j.out    # Standard output file
#SBATCH --error=./scratch/p2-output/dp%j.err     # Error file
#SBATCH --partition=ice-gpu         # Partition name (check with 'sinfo' if needed)
#SBATCH -N1 --gres=gpu:1       # Request 1 GPU
#SBATCH --cpus-per-task=4           # Request 4 CPU cores
#SBATCH --mem=32G                   # Request 16GB RAM
#SBATCH --time=01:00:00             # Max job runtime (hh:mm:ss)

# Load necessary modules (modify as per your HPC environment)
module load anaconda3  # If Conda is available
. /storage/ice1/7/1/mong31/conda3/etc/profile.d/conda.sh
conda activate my_env  # Activate your Conda environment

export HUGGINGFACE_TOKEN=$(cat /home/hice1/mong31/scratch/hf-token.env)

# Run the DeepSeek Python script
python seek_test.py --prompt "${escapedPrompt}"`;

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
      setOutput('');
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

      if (data.state === "COMPLETED") {
        fetchOutput();
      }
    } else {
      alert("Error checking job: " + data.detail);
    }
  }

  async function fetchOutput() {
    const response = await fetch(`http://localhost:8000/jobs/${jobId}/output`);
    const data = await response.json();

    if (response.ok) {
      setOutput(data.output);
    } else {
      alert("Error fetching output: " + data.detail);
    }
  }

  //xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

  return (
    <div className="App" style={{ maxWidth: '600px', margin: 'auto', padding: '2rem' }}> 
      <h1>DeepSeek Chat</h1>
      <textarea
        value={prompt}
        onChange={e => setPrompt(e.target.value)}
        placeholder="Enter your prompt..."
        rows={8}
        cols={60}
        style={{ width: '100%', marginBottom: '1rem' }}
      />
      <br />
      <button onClick={submitJob}>Submit Job</button>
      {jobId && (
        <div style={{marginTop: '1rem'}}>
          <h3>{status}</h3>
          <button onClick={checkStatus}>Check Status</button>
        </div>
      )}
      {output && (
        <div className="outputBox" style={{ whiteSpace: 'pre-wrap', marginTop: '1rem' }}>
          <h4>Assistant Response:</h4>
          <pre>{output}</pre>
        </div>
      )}
    </div>
  );
}

export default App;