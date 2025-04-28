import { useState } from 'react';

function App() {
  const [prompt, setPrompt] = useState('');
  const [jobId, setJobId]   = useState('');
  const [status, setStatus] = useState('');
  const [output, setOutput] = useState('');

  async function submitJob() {
    if (!prompt.trim()) {
      alert("Please enter a prompt!");
      return;
    }

    const escapedPrompt = prompt.replace(/"/g, '\\"');

    const script = `#!/bin/bash
#SBATCH --job-name=deepseek_test
#SBATCH --output=dp%j.out
#SBATCH --error=dp%j.err
#SBATCH --partition=ice-gpu
#SBATCH -N1 --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=ychauhan9@gatech.edu

module load anaconda3
source activate my_env

export HUGGINGFACE_TOKEN=$(cat /home/hice1/ychauhan9/scratch/hgtoken.env)

python seek_test.py --prompt "${escapedPrompt}"`;

    const script2 = `#!/bin/bash
    #SBATCH --job-name=deepseek_test    # Job name
    #SBATCH --output=./scratch/dp%j.out    # Standard output file
    #SBATCH --error=./scratch/dp%j.err     # Error file
    #SBATCH --partition=ice-gpu         # Partition name (check with 'sinfo' if needed)
    #SBATCH -N1 --gres=gpu:4       # Request 4 GPU
    #SBATCH --cpus-per-task=4           # Request 4 CPU cores
    #SBATCH --mem=32G                   # Request 16GB RAM
    #SBATCH --time=01:00:00             # Max job runtime (hh:mm:ss)
    
    # Load necessary modules (modify as per your HPC environment)
    module load anaconda3  # If Conda is available
    source activate my_env  # Activate your Conda environment
    
    export HUGGINGFACE_TOKEN=$(cat /home/hice1/ychauhan9/scratch/hgtoken.env)
    
    # Run the DeepSpeed
    
    deepspeed --num_gpus=4 --local_rank=1 ds-seek-test.py --prompt "${escapedPrompt}"`;

    const response = await fetch("http://localhost:8000/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ script })
    });
    const data = await response.json();

    if (response.ok) {
      setJobId(data.job_id);
      setStatus(`Job submitted! ID: ${data.job_id}`);
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
      setStatus(`Job ${jobId} is currently: ${data.state}`);
      if (data.state === 'COMPLETED') {
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

  return (
    <div className="App" style={{ maxWidth: 600, margin: 'auto', padding: '2rem' }}>
      <h1>DeepSeek Chat</h1>
      <textarea
        value={prompt}
        onChange={e => setPrompt(e.target.value)}
        placeholder="Enter your prompt..."
        rows={8}
        cols={60}
        style={{ width: '100%', marginBottom: '1rem' }}
      />
      <button onClick={submitJob}>Submit Job</button>

      {jobId && (
        <div style={{ marginTop: '1rem' }}>
          <h3>{status}</h3>
          <button onClick={checkStatus}>Check Status</button>
        </div>
      )}

      {output && (
        <div style={{ whiteSpace: 'pre-wrap', marginTop: '1rem' }}>
          <h4>Assistant Response:</h4>
          <pre>{output}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
