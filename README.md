Since we are using a different model now, I deleted the old environment and created a new one. I also updated `requirement.txt` which stores all the dependencies needed for our project.

Ok, so what to do now:
1. delete old environment - `llama-env`
    - for me (macOS), I just went on Finder to look for Macintosh HD/opt/homebrew/Caskroom/miniconda/base, and delete the `llama-env` folder inside the directory.
2. create a new Python environment `ai-model` and install all required dependencies from `requirement.txt`:
``` shell
conda create -n ai-model python=3.10
conda activate ai-model
pip install -r requirements.txt
```

# A simple walkthrough: Run and Test the DeepSeek API
```scss
  You (User) 
      ↓
  ┌────────────────────────┐
  │ 1. Send request to API  │  ← (example: POST /jobs with a script)
  └────────────────────────┘
      ↓
  ┌───────────────────────────────────┐
  │ 2. FastAPI (app.py) receives it   │
  │    and calls slurm_cli functions  │
  └───────────────────────────────────┘
      ↓
  ┌──────────────────────────────────────┐
  │ 3. slurm_cli.py connects to ICE HPC  │
  │    using SSH via paramiko            │
  │    - submits job (sbatch)             │
  │    - checks job state (squeue)        │
  │    - cancels job (scancel)            │
  └──────────────────────────────────────┘
      ↓
  ┌───────────────────────────────┐
  │ 4. ICE HPC schedules and runs │
  │    the DeepSeek code (seek_test.py)   │
  └───────────────────────────────┘
      ↓
  ┌──────────────────────────────────────────────┐
  │ 5. Output saved into dp<jobid>.out or .err files│
  │    (in your ICE account scratch space)         │
  └──────────────────────────────────────────────┘

```
1. Enter Python environment: `conda activate ai-model`
2. cd to `backend` 
3. Install Python packages: `pip install -r requirements.txt`
4. Start the *FastAPI* server:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
5. Submit a Job from Terminal using curl:
	- open a second Terminal window (keep the first one running FastAPI server)
	- cd to the `backend` directory again
    - go to `slurm_cli.py` line ~24, add your username
    - if you haven't got a SSH key, create one using:
```bash
ssh-keygen -t rsa -b 4096 -C "gt-username@login-ice.pace.gatech.edu"
```
    - Upload the public key to ICE:
```bash
ssh-copy-id gt-username@login-ice.pace.gatech.edu
```
    - Submit a job to ICE:
```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d @dp_batch.json
```
6. You should see this output after a few seconds:
```json
{"job_id":"2538690","state":"PENDING"}
```

# Running full client with UI
1. run the backend:
    - cd to `backend`:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
2. run the frontend:
    - cd to `frontend`:
```bash
npm run dev
```
3. copy the address shown (should be http://localhost:5173/)

Note: It'll take a while to see the output after clicking **Submit Job** button
