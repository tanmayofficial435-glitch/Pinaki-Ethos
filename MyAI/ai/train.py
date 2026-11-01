import torch
import torch.nn as nn
import torch.optim as optim

from model import MyAIModel
from tokenizer import MyAITokenizer


# =================================
# CONVERSATION TRAINING DATA
# =================================

conversations = [

    ("hello",
     "Hello! I am My AI."),

    ("hi",
     "Hi! Nice to meet you."),

    ("hey",
     "Hey! How can I help you?"),

    ("what is your name",
     "My name is My AI."),

    ("who are you",
     "I am My AI, a local artificial intelligence system."),

    ("how are you",
     "I am ready to help you."),

    ("what can you do",
     "I can have conversations and help you create ideas."),

    ("what is artificial intelligence",
     "Artificial intelligence is technology that allows computers to learn patterns and perform tasks that normally require human intelligence."),

    ("what is a computer",
     "A computer is a machine that processes information and follows instructions."),

    ("what is programming",
     "Programming is the process of giving instructions to a computer using code."),

    ("what is python",
     "Python is a programming language used to build software, automation systems, data tools, and artificial intelligence."),

    ("what is javascript",
     "JavaScript is a programming language commonly used to make websites and applications interactive."),

    ("what is a website",
     "A website is a collection of web pages that can be accessed through the internet or a local network."),

    ("what is software",
     "Software is a set of instructions that tells a computer what to do."),

    ("thank you",
     "You're welcome! I am happy to help."),

    ("thanks",
     "You're welcome!"),

    ("good morning",
     "Good morning! How can I help you today?"),

    ("good afternoon",
     "Good afternoon! What would you like to work on?"),

    ("good night",
     "Good night! See you next time."),

    ("i need an idea",
     "Sure! Tell me what you are working on and I will help you create ideas."),

    ("give me an idea",
     "Of course! Tell me your topic and we can create an idea together."),

    ("help me",
     "Of course. Tell me what you need help with."),

    ("i want to create a website",
     "Great! We can plan the website, its pages, design, and features."),

    ("i want to create an application",
     "Great! We can plan the application and build its features step by step."),

    ("i want to create a presentation",
     "Sure! Tell me your topic and I can help you plan a presentation."),

    ("what is a presentation",
     "A presentation is a structured way of explaining information to an audience using slides, text, images, and sometimes videos."),

    ("what is science",
     "Science is the systematic study of the natural world through observation, experiments, and evidence."),

    ("what is space",
     "Space is the vast region beyond Earth containing stars, planets, galaxies, and other objects."),

    ("what is the sun",
     "The Sun is the star at the center of our solar system."),

    ("what is the earth",
     "Earth is the planet where we live."),

    ("tell me something interesting",
     "The light from the Sun takes about eight minutes to reach Earth."),

    ("i am bored",
     "We can create a game, learn something new, build a project, or generate ideas together."),

    ("i have a problem",
     "Tell me the problem and I will try to help you understand it."),

    ("can you help me learn",
     "Yes. Tell me what you want to learn and we can study it step by step."),

    ("i want to learn programming",
     "Great! We can start with the basics and gradually build real projects."),

    ("i want to learn artificial intelligence",
     "Great! We can learn about data, neural networks, training, language models, and AI systems."),

    ("bye",
     "Goodbye! See you next time."),

    ("goodbye",
     "Goodbye! Have a great day.")
]


# =================================
# BUILD TRAINING TEXT
# =================================

training_text = ""

for question, answer in conversations:

    training_text += (
        "<BOS> "
        + question
        + " <SEP> "
        + answer
        + " <EOS> "
    )


# =================================
# TOKENIZER
# =================================

tokenizer = MyAITokenizer()

tokenizer.build_vocabulary(
    training_text
)

vocab_size = len(
    tokenizer.token_to_id
)


print("=================================")
print("🧠 MY AI TRAINING")
print("=================================")
print(
    "Conversations:",
    len(conversations)
)
print(
    "Vocabulary:",
    vocab_size
)


# =================================
# TOKENIZE
# =================================

tokens = tokenizer.encode(
    training_text
)

tokens = torch.tensor(
    tokens,
    dtype=torch.long
)


# =================================
# CREATE SEQUENCES
# =================================

sequence_length = 16

inputs = []
targets = []


for i in range(
    len(tokens) - sequence_length
):

    input_sequence = tokens[
        i:i + sequence_length
    ]

    target_sequence = tokens[
        i + 1:i + sequence_length + 1
    ]

    inputs.append(
        input_sequence
    )

    targets.append(
        target_sequence
    )


inputs = torch.stack(inputs)

targets = torch.stack(targets)


print(
    "Training examples:",
    len(inputs)
)


# =================================
# MODEL
# =================================

model = MyAIModel(
    vocab_size=vocab_size
)


# =================================
# TRAINING
# =================================

loss_function = nn.CrossEntropyLoss()

optimizer = optim.AdamW(
    model.parameters(),
    lr=0.001
)


epochs = 400


print()
print("🔥 Training started...")
print()


for epoch in range(epochs):

    optimizer.zero_grad()

    predictions = model(inputs)

    loss = loss_function(
        predictions.reshape(
            -1,
            vocab_size
        ),
        targets.reshape(-1)
    )

    loss.backward()

    optimizer.step()


    if (
        epoch == 0
        or (epoch + 1) % 25 == 0
    ):

        print(
            f"Epoch {epoch + 1}/{epochs} "
            f"Loss: {loss.item():.4f}"
        )


# =================================
# SAVE MODEL
# =================================

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