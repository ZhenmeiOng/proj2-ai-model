# slurm_cli.py
"""Thin wrapper around sbatch/squeue/scancel using one persistent
Paramiko SSH connection."""

import paramiko, getpass, threading
from typing import Optional
import shlex

_client_lock = threading.Lock()
_client: Optional[paramiko.SSHClient] = None

def _get_client() -> paramiko.SSHClient:
    """Return a singleton Paramiko client (opens first time)."""
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = paramiko.SSHClient()
                _client.load_system_host_keys()
                _client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                _client.connect(
                    hostname='login-ice.pace.gatech.edu',
                    username="mong31", # replace your username
                    allow_agent=True,
                    look_for_keys=True
                )
    return _client

def deepseek_infer(prompt: str, script_text: str) -> str:
    """
    Run the DeepSeek inference script on the login node and
    return the model's reply as plain text.
    `script` could be any Python file that prints just the answer.
    """
    ssh = _get_client()                # ← already handles reconnect
    #safe_prompt = shlex.quote(prompt)  # avoid shell injection
    stdin, stdout, stderr = ssh.exec_command("sbatch --parsable")
    stdin.write(script_text)
    stdin.channel.shutdown_write()
    reply = stdout.read().decode()
    err   = stderr.read().decode()
    if err and not reply.strip():
        raise RuntimeError(err)
    return reply.strip()

def submit(script_text: str) -> str:
    """Submit a batch script via stdin. Returns job ID (str)."""
    ssh = _get_client()
    stdin, stdout, stderr = ssh.exec_command("sbatch --parsable")
    stdin.write(script_text)
    stdin.channel.shutdown_write()
    job_id = stdout.read().decode().strip()
    err = stderr.read().decode()
    if err:
        raise RuntimeError(err)
    return job_id

def job_state(job_id: str) -> str:
    """Return SLURM job state (e.g., PENDING, RUNNING, COMPLETED)."""
    ssh = _get_client()
    cmd = f"squeue -h -j {job_id} -o '%T'"
    _, stdout, stderr = ssh.exec_command(cmd)
    state = stdout.read().decode().strip()
    err = stderr.read().decode()
    if err and not state:
        raise RuntimeError(err)
    return state or "COMPLETED"

def cancel(job_id: str) -> None:
    ssh = _get_client()
    _, _, stderr = ssh.exec_command(f"scancel {job_id}")
    err = stderr.read().decode()
    if err:
        raise RuntimeError(err)

def get_output(job_id: str, prefix: str = "dp") -> str:
    """
    Fetch the SLURM job's stdout output file and return its contents.
    By default, this reads 'dp<job_id>.out' in the submission directory.
    """
    ssh = _get_client()
    filename = f"./scratch/p2-output/{prefix}{job_id}.out"
    cmd = f"cat {shlex.quote(filename)}"
    _, stdout, stderr = ssh.exec_command(cmd)
    content = stdout.read().decode()
    
    err = stderr.read().decode()
    if err:
        if "No such file or directory" in err:
            raise FileNotFoundError(f"Output file '{filename}' not found.")
        else:
            raise RuntimeError(err)
    return content
