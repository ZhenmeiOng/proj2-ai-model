# to be run on ICE
from transformers import AutoTokenizer, AutoModelForCausalLM

local_directory = "../deepseek-model" 

model = AutoModelForCausalLM.from_pretrained("deepseek-ai/deepseek-math-7b-instruct", cache_dir=local_directory)
tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/deepseek-math-7b-instruct", cache_dir=local_directory)

print("Model installed successfully")

