from transformers import GPTNeoForCausalLM, AutoTokenizer

# Load the fine-tuned model and tokenizer
model_path = r"C:\Users\ndeyf\Documents\human needs\project\fine_tuned_gpt_neo"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = GPTNeoForCausalLM.from_pretrained(model_path)

# Generate predictions
def generate_response(prompt, max_length=150,  top_k=50):
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    output = model.generate(
        input_ids=input_ids,
        max_length=max_length,
        top_k=top_k,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=False
    )
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    return response

# Test the fine-tuned model
prompt = "Question:what  ?\nAnswer:"
response = generate_response(prompt)
print(response)
