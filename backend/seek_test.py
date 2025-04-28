# upload this file to ICE

import argparse
import torch
from pathlib import Path
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    GenerationConfig,
)
 
# ── 1. Parse the user's prompt from CLI ────────────────────────────────────────
parser = argparse.ArgumentParser(description="Run DeepSeek with a custom prompt")
parser.add_argument(
    "--prompt",
    type=str,
    required=True,
    help="The user prompt to send to DeepSeek",
)
parser.add_argument(
    "--model-dir",
    type=str,
    default="/home/hice1/mong31/scratch/deepseek-model/models--deepseek-ai--deepseek-math-7b-instruct/snapshots/0a5828f800a36df0fd7f0ed581b983246c0677ff",
    help="Path to the local DeepSeek model directory",
)
args = parser.parse_args()
PROMPT = args.prompt
MODEL_DIR = Path(args.model_dir)
 
# ── 2. Load tokenizer ─────────────────────────────────────────────────────────
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
 
# Ensure a pad token is available
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.pad_token_id = tokenizer.eos_token_id
 
# ── 3. Load the model (GPU if available, CPU fallback) ────────────────────────
model = AutoModelForCausalLM.from_pretrained(
    MODEL_DIR,
    torch_dtype="auto",          # bf16/fp16 if the GPU supports it
    device_map="auto",           # splits across GPUs if multiple are visible
    low_cpu_mem_usage=True,      # streaming load to reduce RAM
    local_files_only=True,
)
 
# ── 4. Load generation config ─────────────────────────────────────────────────
generation_config = GenerationConfig.from_pretrained(
    MODEL_DIR, local_files_only=True
)
generation_config.pad_token_id = tokenizer.pad_token_id
 
# ── 5. Build the chat template ────────────────────────────────────────────────
messages = [
    {"role": "user", "content": PROMPT}
]
inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    return_tensors="pt"
)
attention_mask = inputs.ne(tokenizer.pad_token_id).long()
 
# Move tensors to the model device
inputs, attention_mask = inputs.to(model.device), attention_mask.to(model.device)
 
# ── 6. Generate a reply ───────────────────────────────────────────────────────
with torch.no_grad():
    outputs = model.generate(
        input_ids=inputs,
        attention_mask=attention_mask,
        max_new_tokens=128,
        pad_token_id=generation_config.pad_token_id,
    )
 
reply = tokenizer.decode(
    outputs[0][inputs.shape[1]:],
    skip_special_tokens=True
)
 
print("\nAssistant:", reply)