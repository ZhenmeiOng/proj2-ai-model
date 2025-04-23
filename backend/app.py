# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from slurm_cli import submit, job_state, cancel, deepseek_infer

app = FastAPI(title="Slurm CLI Gateway API")

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
