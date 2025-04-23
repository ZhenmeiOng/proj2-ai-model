import torch
import argparse
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig

# Define model name
MODEL_NAME = "deepseek-ai/deepseek-math-7b-instruct"

parser = argparse.ArgumentParser(
    description="Query DeepSeek-Math-7B-Instruct from the command line"
)
parser.add_argument(
    "--prompt",
    type=str,
    required=True,
    help="Natural-language question or instruction for the model.",
)
parser.add_argument(
    "--max_new_tokens",
    type=int,
    default=512,
    help="Maximum tokens to generate beyond the prompt.",
)
args = parser.parse_args()

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token  # Set the EOS token as padding
    tokenizer.pad_token_id = tokenizer.eos_token_id

# Load model with bfloat16 precision and auto device placement
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.bfloat16, device_map="auto")

# Load generation configuration and set pad_token_id
generation_config = GenerationConfig.from_pretrained(MODEL_NAME)
generation_config.pad_token_id = generation_config.eos_token_id  # Ensure proper padding behavior

# Define the chat-based prompt
messages = [
    {"role": "user", "content": args.prompt}
]

# Tokenize input and request attention_mask
input_tensor = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")

attention_mask = input_tensor.ne(tokenizer.pad_token_id).long()  # Creates a mask where 1 = real token, 0 = padding

# Generate response with attention_mask
outputs = model.generate(
    input_ids=input_tensor.to(model.device),
    attention_mask=attention_mask.to(model.device),  # Ensure attention_mask is used
    max_new_tokens=1000,
    pad_token_id=generation_config.eos_token_id
)

# Decode generated response
result = tokenizer.decode(outputs[0][input_tensor.shape[1]:], skip_special_tokens=True)
print(result.strip())