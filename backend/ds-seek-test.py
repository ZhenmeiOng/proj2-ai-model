# upload to ICE - deepSpeed

# monkey-patch LlamaAttention so DS can find .num_heads
from transformers.models.llama.modeling_llama import LlamaAttention
# whenever someone does llama_attn.num_attention_heads → forward to config
setattr(
    LlamaAttention,
    "num_attention_heads",
    property(lambda self: self.config.num_attention_heads)
)
# and make num_heads an alias for the same thing
setattr(
    LlamaAttention,
    "num_heads",
    property(lambda self: self.config.num_attention_heads)
)
setattr(
    LlamaAttention,
    "rope_theta",
    property(lambda self: getattr(self.config, "rope_theta", 10000.0))
)

import argparse
import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
import deepspeed

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
# ← add this so DS launcher args are swallowed:
parser.add_argument("--local_rank", type=int, default=0, help="DeepSpeed process rank")
args = parser.parse_args()

if torch.cuda.is_available():
    # bind this process to the GPU that DeepSpeed assigned via --local_rank
    torch.cuda.set_device(args.local_rank)
    device = torch.device("cuda")
else:
    device = torch.device("cpu")

PROMPT = args.prompt
MODEL_DIR = Path(args.model_dir)
 
# ── 2. Load tokenizer ─────────────────────────────────────────────────────────
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
 
# Ensure a pad token is available
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.pad_token_id = tokenizer.eos_token_id
 
 # ── 2a. Load generation config for chat/sampling settings ────────────────────
generation_config = GenerationConfig.from_pretrained(
    MODEL_DIR,
    local_files_only=True
)
# ensure pad/eos are set
generation_config.pad_token_id = tokenizer.pad_token_id
generation_config.eos_token_id = tokenizer.eos_token_id

# ── 3. Load the model (GPU if available, CPU fallback) ────────────────────────
model = AutoModelForCausalLM.from_pretrained(
    MODEL_DIR,
    torch_dtype=torch.bfloat16,          # bf16/fp16 if the GPU supports it
    # device_map="auto",           # splits across GPUs if multiple are visible
    # low_cpu_mem_usage=True,      # streaming load to reduce RAM
    local_files_only=True,
)

# ── 4. Wrap with DeepSpeed inference ─────────────────────────────
model = deepspeed.init_inference(
    model,  
    mp_size=1,                       # single-GPU
    dtype=torch.bfloat16,            
    replace_method="auto",           
    replace_with_kernel_inject=True,
)

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
# inputs, attention_mask = inputs.to(model.device), attention_mask.to(model.device)
inputs         = inputs.to(device)
attention_mask = attention_mask.to(device)


# ── 6. Generate ────────────────────────────────────────────────
with torch.no_grad():
    outputs = model.generate(
        input_ids=inputs,
        attention_mask=attention_mask,

        # ← use your loaded chat settings:
        max_new_tokens       = generation_config.max_new_tokens,
        do_sample            = generation_config.do_sample,
        temperature          = generation_config.temperature,
        top_p                = generation_config.top_p,
        repetition_penalty   = generation_config.repetition_penalty,
        eos_token_id         = generation_config.eos_token_id,
        pad_token_id         = generation_config.pad_token_id,
    )

# ── 7. Decode & print ────────────────────────────────────────────
reply = tokenizer.decode(
    outputs[0][inputs.shape[1]:],
    skip_special_tokens=True
)
if args.local_rank == 0:
    print("\nAssistant:", reply.strip())
