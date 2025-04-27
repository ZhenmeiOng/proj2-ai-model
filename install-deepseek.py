from transformers import AutoTokenizer, AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("deepseek-ai/deepseek-math-7b-instruct")
tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/deepseek-math-7b-instruct")

