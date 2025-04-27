# app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse

from slurm_cli import submit, job_state, cancel, deepseek_infer, get_output

app = FastAPI(title="Slurm CLI Gateway API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (safe for localhost dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Prompt(BaseModel):
    prompt: str

class Answer(BaseModel):
    answer: str

class JobSubmit(BaseModel):
    script: str

class JobInfo(BaseModel):
    job_id: str
    state: str

@app.post("/deepseek", response_model=Answer)
def run_deepseek(req: JobSubmit):
    try:
        ans = deepseek_infer(req.script)
        return Answer(answer=ans)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/jobs", response_model=JobInfo)
def submit_job(req: JobSubmit):
    try:
        jid = submit(req.script)
        return JobInfo(job_id=jid, state=job_state(jid))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}", response_model=JobInfo)
def get_status(job_id: str):
    try:
        return JobInfo(job_id=job_id, state=job_state(job_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/jobs/{job_id}")
def cancel_job(job_id: str):
    try:
        cancel(job_id)
        return {"detail": "canceled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}/output")
async def read_job_output(job_id: str):
     try:
         raw = get_output(job_id)
     except FileNotFoundError:
         raise HTTPException(status_code=404, detail=f"Output for job {job_id} not found.")
     except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
 
     # Extract the Assistant block
     start_idx = raw.find("Assistant:")
     if start_idx != -1:
         delim_idx = raw.find("---", start_idx)
         block = raw[start_idx:delim_idx] if delim_idx != -1 else raw[start_idx:]
     else:
         block = raw
 
     reply = block.strip()
 
     # Wrap every 15 words into new lines
     words = reply.split()
     lines = [' '.join(words[i:i+15]) for i in range(0, len(words), 15)]
     wrapped = '\n'.join(lines)
 
     return {"job_id": job_id, "output": wrapped}
