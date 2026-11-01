import torch
import torch.nn as nn
import torch.optim as optim

from model import MyAIModel
from tokenizer import MyAITokenizer


# =========================================
# TRAINING DATA
# =========================================

training_text = """
Hello.
Hello! I am My AI.

Hi.
Hi! Nice to meet you.

What is your name?
My name is My AI.

How are you?
I am ready to help you.

What can you do?
I can have conversations and help you create ideas.

What is artificial intelligence?
Artificial intelligence allows computers to perform tasks that normally require human intelligence.

What is a computer?
A computer is a machine that processes information and follows instructions.

Thank you.
You're welcome!

Good morning.
Good morning! How can I help you?

Good night.
Good night! See you next time.

I need an idea.
Sure! Tell me what you are working on and I will help you create ideas.

Help me.
Of course. Tell me what you need help with.

I want to create a presentation.
Sure! Tell me your topic and I can help you plan a presentation.
"""


# =========================================
# CREATE TOKENIZER
# =========================================

tokenizer = MyAITokenizer()

tokenizer.build_vocabulary(training_text)

vocab_size = len(tokenizer.token_to_id)

print("=================================")
print("🧠 MY AI TRAINING")
print("=================================")
print("Vocabulary:", vocab_size)


# =========================================
# CONVERT TEXT TO NUMBERS
# =========================================

tokens = tokenizer.encode(training_text)

tokens = torch.tensor(
    tokens,
    dtype=torch.long
)


# =========================================
# CREATE TRAINING EXAMPLES
# =========================================

sequence_length = 4

inputs = []
targets = []

for i in range(
    len(tokens) - sequence_length
):

    input_sequence = tokens[
        i:i + sequence_length
    ]

    target = tokens[
        i + sequence_length
    ]

    inputs.append(input_sequence)
    targets.append(target)


inputs = torch.stack(inputs)

targets = torch.tensor(
    targets,
    dtype=torch.long
)


print("Training examples:", len(inputs))


# =========================================
# CREATE MODEL
# =========================================

model = MyAIModel(
    vocab_size=vocab_size
)


# =========================================
# TRAINING SETUP
# =========================================

loss_function = nn.CrossEntropyLoss()

optimizer = optim.Adam(
    model.parameters(),
    lr=0.001
)


# =========================================
# TRAIN
# =========================================

epochs = 100

print()
print("🔥 Training started...")
print()

for epoch in range(epochs):

    optimizer.zero_grad()

    predictions = model(inputs)

    loss = loss_function(
        predictions,
        targets
    )

    loss.backward()

    optimizer.step()

    if (
        epoch == 0
        or (epoch + 1) % 10 == 0
    ):

        print(
            f"Epoch {epoch + 1}/{epochs} "
            f"Loss: {loss.item():.4f}"
        )


# =========================================
# SAVE MODEL
# =========================================

torch.save(
    model.state_dict(),
    "ai/my_ai_model.pth"
)

tokenizer.save(
    "ai/tokenizer.json"
)


print()
print("=================================")
print("✅ TRAINING COMPLETE")
print("=================================")
print("Model saved:")
print("ai/my_ai_model.pth")
print()
print("Tokenizer saved:")
print("ai/tokenizer.json")
print("=================================")