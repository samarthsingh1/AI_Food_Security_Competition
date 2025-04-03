from transformers import T5Tokenizer, T5ForConditionalGeneration

# Load FLAN-T5 base model
model_name = "google/flan-t5-small"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

def generate_summary(text):
    prompt = f"Summarize this customer request in one sentence: {text.strip()}"
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    output = model.generate(input_ids, max_length=40, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(output[0], skip_special_tokens=True)
    return summary

test_text = "Hi, I just moved here and I’m trying to get assistance for my family. Is there a way to schedule a pantry visit this weekend?"
print("Summary:", generate_summary(test_text))
