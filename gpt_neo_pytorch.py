from transformers import GPTNeoForCausalLM, AutoTokenizer, Trainer, TrainingArguments, DataCollatorForSeq2Seq
from datasets import load_dataset
import pandas as pd
import os

# Step 1: Save your dataset to a CSV file with Input and Response columns
data = {
    "Input": [
        "What is the 6P method?",
        "What is the balance of all entities in the 6P method for this project?",
        "How can I improve the score for Planet?",
        "What are the six components of the 6P method?",
        "How does the 6P method support sustainability?",
        "Can you explain the role of People in the 6P method?",
        "What does Planet focus on in the 6P method?",
        "How is Potentials defined in the 6P method?",
        "What is the significance of Proliferation in the 6P framework?",
        "What does Possibilities mean in the 6P method?",
        "How do Particularities shape decision-making in the 6P method?",
        "How do the 6P entities interact with each other?",
        "Why is the balance of all 6Ps important?",
        "How can I improve the score for People in my project?",
        "What strategies can improve the Planet score in the 6P method?",
        "How can organizations use the 6P method for better decision-making?",
        "What is an example of using the 6P method in real-life projects?",
        "How does the 6P method differ from traditional frameworks?",
        "What are common challenges when applying the 6P method?",
        "What tools can help implement the 6P method effectively?",
        "Can the 6P method be customized for specific industries?",
        "What are the key benefits of using the 6P method?",
        "How can I measure the success of a 6P-based project?",
        "What are practical examples of balancing Planet and People?",
        "How does the 6P method address future potentials?",
        "What is the purpose of the 6P method in sustainable design?",
        "Can you explain how the 6P method relates to innovation?",
        "What is the difference between Planet and Possibilities?",
        "How do you ensure that all 6Ps are balanced in a project?",
        "Why is Proliferation important for scaling solutions?",
        "What does it mean to align Particularities with other Ps?",
        "Can the 6P method help with reducing environmental impact?",
        "How do you identify trade-offs in the 6P framework?",
        "What is the primary need driving the change in building design?",
        "How should the building world respond to changing needs?",
        "What is the goal of constructing new buildings in light of current trends?",
        "Who developed the 6P method, and what was its purpose?",
        "What is the first step in the 6P methodology?",
        "What tool is used in the 6P method to separate the design into layers?",
        "What perspectives are considered in the 6P method?",
        "How do the inside and outside perspectives relate in the 6P method?",
        "How are the layers in the 6P method evaluated?",
        "What is the benefit of separating design into six layers?",
    ],
    "Response": [
        "The 6P method is a framework that focuses on balancing the 6 human needs: People, Planet, Potentials, Proliferation, Possibilities, and Particularities in a project.",
        "The balance of all entities depends on the project's current metrics: Planet: 40%, People: 15%, Potentials: 6%, Proliferation: 4%, Possibilities: 25%, Particularities: 10%.",
        "Planet already has a high score of 40%. To improve it further, consider reducing waste, increasing recycling, and promoting sustainable practices.",
        "The 6P method consists of People, Planet, Potentials, Proliferation, Possibilities, and Particularities.",
        "The 6P method integrates human needs and environmental priorities, supporting long-term sustainability.",
        "People focuses on the individuals and communities impacted by the project, ensuring equity and inclusivity.",
        "Planet emphasizes minimizing environmental impact and preserving natural resources for future generations.",
        "Potentials refer to the opportunities for growth, innovation, and future possibilities within a project.",
        "Proliferation involves scaling solutions and sharing innovations to amplify positive impact.",
        "Possibilities explore creative approaches and innovative ideas that address project challenges.",
        "Particularities consider the unique context, needs, and constraints of a specific project or situation.",
        "The 6Ps work as an interconnected system where changes in one entity affect the others.",
        "Balancing all 6Ps ensures that no single component is prioritized at the expense of others.",
        "You can improve People by engaging stakeholders, prioritizing diversity, and ensuring fairness.",
        "Strategies like using renewable resources and reducing emissions can improve the Planet score.",
        "Organizations can use the 6P method to align projects with sustainability and human needs.",
        "An example would be a green building project that prioritizes all six components of the 6P method.",
        "The 6P method incorporates holistic and systemic thinking, unlike traditional linear frameworks.",
        "Common challenges include balancing competing priorities and aligning all stakeholders.",
        "Tools like lifecycle analysis and stakeholder mapping can support the 6P method.",
        "Yes, the 6P method can be tailored to specific sectors like construction or manufacturing.",
        "The 6P method enhances decision-making, fosters innovation, and promotes sustainability.",
        "You can measure success using metrics aligned with each P, such as stakeholder satisfaction and emissions reductions.",
        "Practical examples include using green technologies to balance environmental goals and community well-being.",
        "The 6P method ensures future potentials are preserved by focusing on long-term impact.",
        "Its purpose is to balance human, environmental, and contextual needs in design and decision-making.",
        "The 6P method fosters innovation by encouraging exploration of diverse ideas and solutions.",
        "Planet focuses on the environment, while Possibilities encourage creativity and innovative thinking.",
        "Balance is achieved by evaluating trade-offs and ensuring alignment between all components.",
        "Proliferation ensures innovations are scaled and shared for broader adoption and impact.",
        "Aligning Particularities ensures project-specific needs are considered alongside global priorities.",
        "Yes, by focusing on Planet and other Ps, the method promotes reduced environmental impact.",
        "Trade-offs are identified by analyzing the impact of decisions on all 6Ps and finding compromises.",
        "The human need for buildings to live, work, and learn is changing due to developments in sustainability, climate adaptation, viruses, and population growth.",
        "The building world should respond by cooperating more closely and with greater commitment with residents, users, social platforms, and designers.",
        "The goal is to build constructions that suit the wishes and requirements of our time while considering a future that can change very quickly.",
        "Dr. Ron de Vrieze developed the 6P method during his PhD study to facilitate joined design processes and address changing building needs.",
        "The first step is to separate various interests at different levels to create a better overview and balance the integration of design and process.",
        "Open Building is used to separate the design into six different layers, from workplace to neighborhood level.",
        "The method considers the end-user perspective (from the inside looking out) and the social perspective (from the outside looking in).",
        "These perspectives merge in a 'skin' that resembles dome constructions, where the various interests between inside and outside gradually merge.",
        "The layers are weighed on their subjective and objective value using the 6P method.",
        "Separating design into six layers allows the integration of design and process to be balanced, incorporating both the end-user and social perspectives.",
    ]
}

# Save to CSV
csv_path = "6p_dataset.csv"
df = pd.DataFrame(data)
df.to_csv(csv_path, index=False)

print(f"Dataset saved to {csv_path}")

# Step 2: Load the dataset into Hugging Face's Datasets library
dataset = load_dataset("csv", data_files=csv_path)

# Step 3: Split the dataset into train and validation (evaluation) datasets
dataset = dataset["train"].train_test_split(test_size=0.2)  # 80% train, 20% validation

# Step 4: Load tokenizer
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neo-1.3B")
tokenizer.pad_token = tokenizer.eos_token  # Set pad_token to eos_token

# Step 5: Preprocess function (concatenate Input and Response for training)
def preprocess_function(examples):
    inputs = examples['Input']
    responses = examples['Response']
    # Concatenate input and response with a separator
    prompts = [f"Question: {input_}\nAnswer: {response}" for input_, response in zip(inputs, responses)]
    
    # Tokenize with padding and truncation
    tokenized_inputs = tokenizer(
        prompts,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt"
    )
    
    # Set labels equal to input_ids for causal language modeling
    tokenized_inputs["labels"] = tokenized_inputs["input_ids"]
    
    return {
        "input_ids": tokenized_inputs["input_ids"],
        "attention_mask": tokenized_inputs["attention_mask"],
        "labels": tokenized_inputs["labels"]
    }

# Step 6: Tokenize the dataset
tokenized_dataset = dataset.map(preprocess_function, batched=True, remove_columns=["Input", "Response"])

# Step 7: Define model and training arguments
model = GPTNeoForCausalLM.from_pretrained("EleutherAI/gpt-neo-1.3B")
# Define data collator for padding
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)
training_args = TrainingArguments(
    output_dir="./results",          # Output directory for model checkpoints
    evaluation_strategy="steps",     # Corrected deprecated field name
    per_device_train_batch_size=2,   # Batch size for training
    per_device_eval_batch_size=2,    # Batch size for evaluation
    num_train_epochs=3,              # Number of epochs
    save_steps=500,                  # Save checkpoint every 500 steps
    save_total_limit=2,              # Limit to 2 checkpoints
    logging_dir="./logs",            # Directory for logs
    logging_steps=100,               # Log every 100 steps
    learning_rate=5e-5,              # Learning rate
    fp16=True,                       # Enable mixed precision for faster training
    push_to_hub=False,               # Set to True if you want to push the model to Hugging Face Hub
    remove_unused_columns=False      # Set this to False if you want to keep unused columns
)

# Step 8: Initialize the Trainer with the evaluation dataset
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["test"],  # Pass the evaluation dataset here
    data_collator=data_collator  # Pass the data collator instead of tokenizer
)

# Step 9: Fine-tune the model
trainer.train()

# Step 10: Save the fine-tuned model
model.save_pretrained(r"C:\Users\ndeyf\Documents\human needs\project\fine_tuned_gpt_neo")
tokenizer.save_pretrained(r"C:\Users\ndeyf\Documents\human needs\project\fine_tuned_gpt_neo")
print("Model fine-tuned and saved successfully!")
