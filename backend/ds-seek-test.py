# # upload to ICE - deepSpeed

# import argparse
# import torch
# from pathlib import Path
# from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
# import deepspeed

# # ── 1. Parse args ────────────────────────────────────────────────
# parser = argparse.ArgumentParser()
# parser.add_argument("--prompt", type=str, required=True)
# parser.add_argument(
#     "--model-dir", type=str,
#     default="/home/hice1/mong31/scratch/deepseek-model/models--deepseek-ai--deepseek-math-7b-instruct/snapshots/0a5828f800a36df0fd7f0ed581b983246c0677ff"
# )
# args = parser.parse_args()
# PROMPT = args.prompt
# MODEL_DIR = Path(args.model_dir)

# # ── 2. Load tokenizer ────────────────────────────────────────────
# tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
# if tokenizer.pad_token is None:
#     tokenizer.pad_token = tokenizer.eos_token
#     tokenizer.pad_token_id = tokenizer.eos_token_id

# # ── 3. Load raw model ────────────────────────────────────────────
# model = AutoModelForCausalLM.from_pretrained(
#     MODEL_DIR,
#     torch_dtype=torch.bfloat16,    # match GPU BF16
#     low_cpu_mem_usage=True,
#     local_files_only=True
# )

# # ── 4. Wrap with DeepSpeed inference ─────────────────────────────
# model = deepspeed.init_inference(
#     model,  
#     mp_size=4,                       # single-GPU
#     dtype=torch.bfloat16,            
#     replace_method="auto",           
#     replace_with_kernel_inject=True  
# )

# # ── 5. Build inputs ──────────────────────────────────────────────
# messages = [{"role": "user", "content": PROMPT}]
# inputs = tokenizer.apply_chat_template(
#     messages, add_generation_prompt=True, return_tensors="pt"
# )
# attention_mask = inputs.ne(tokenizer.pad_token_id).long()
# inputs, attention_mask = (
#     inputs.to(model.device),
#     attention_mask.to(model.device),
# )

# # ── 6. Generate ──────────────────────────────────────────────────
# with torch.no_grad():
#     outputs = model.generate(
#         input_ids=inputs,
#         attention_mask=attention_mask,
#         max_new_tokens=128,
#         pad_token_id=tokenizer.eos_token_id
#     )

# # ── 7. Decode & print ────────────────────────────────────────────
# reply = tokenizer.decode(
#     outputs[0][inputs.shape[1]:],
#     skip_special_tokens=True
# )
# print(reply.strip())


print("hello this is ds-seek-test")