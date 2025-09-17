from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
from trl import SFTTrainer
from datasets import load_dataset
from peft import LoraConfig


model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_4bit=True, # QLoRA
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

dataset = load_dataset("json", data_files="my_dataset.jsonl")

