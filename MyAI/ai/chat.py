import json
from pathlib import Path

import torch

from model import MyAIModel
from tokenizer import MyAITokenizer


# =================================
# FILES
# =================================

MEMORY_FILE = Path("ai/memory.json")


# =================================
# LOAD TOKENIZER
# =================================

tokenizer = MyAITokenizer()
tokenizer.load("ai/tokenizer.json")

vocab_size = len(tokenizer.token_to_id)

EOS_ID = tokenizer.token_to_id["<EOS>"]


# =================================
# LOAD MODEL
# =================================

model = MyAIModel(
    vocab_size=vocab_size
)

model.load_state_dict(
    torch.load(
        "ai/my_ai_model.pth",
        map_location="cpu"
    )
)

model.eval()


# =================================
# MEMORY
# =================================

MAX_HISTORY = 3


def load_memory():
    if not MEMORY_FILE.exists():
        return []

    try:
        data = json.loads(
            MEMORY_FILE.read_text(
                encoding="utf-8"
            )
        )

        if isinstance(data, list):
            return data

    except Exception:
        pass

    return []


def save_memory(history):
    MEMORY_FILE.write_text(
        json.dumps(
            history,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


conversation_history = load_memory()


# =================================
# GENERATE RESPONSE
# =================================

def generate_response(prompt, max_tokens=40):

    context_parts = []

    for item in conversation_history[-MAX_HISTORY:]:
        context_parts.append(
            "<BOS> "
            + item["user"]
            + " <SEP> "
            + item["ai"]
            + " <EOS>"
        )

    context_parts.append(
        "<BOS> "
        + prompt
        + " <SEP>"
    )

    full_prompt = " ".join(context_parts)

    prompt_tokens = tokenizer.encode(
        full_prompt
    )

    generated = prompt_tokens.copy()

    for _ in range(max_tokens):

        input_tokens = generated[-16:]

        input_tensor = torch.tensor(
            [input_tokens],
            dtype=torch.long
        )

        with torch.no_grad():
            output = model(input_tensor)

        logits = output[0, -1]

        next_token = torch.argmax(
            logits
        ).item()

        generated.append(next_token)

        if next_token == EOS_ID:
            break

    new_tokens = generated[
        len(prompt_tokens):
    ]

    if EOS_ID in new_tokens:
        new_tokens = new_tokens[
            :new_tokens.index(EOS_ID)
        ]

    response = tokenizer.decode(
        new_tokens
    ).strip()

    if not response:
        response = "I'm still learning."

    return response


# =================================
# CHAT
# =================================

print("=================================")
print("🧠 MY AI")
print("=================================")
print("Local Transformer loaded.")
print("Persistent memory:", len(conversation_history), "messages")
print("Type 'exit' to stop.")
print("Type 'clear' to erase saved memory.")
print("=================================")
print()


while True:

    user_input = input("You: ").strip()

    if not user_input:
        continue

    if user_input.lower() == "exit":

        save_memory(conversation_history)

        print("My AI: Goodbye! 👋")
        break

    if user_input.lower() == "clear":

        conversation_history.clear()
        save_memory(conversation_history)

        print(
            "My AI: Persistent memory cleared. 🧹"
        )

        continue

    response = generate_response(
        user_input
    )

    conversation_history.append(
        {
            "user": user_input,
            "ai": response
        }
    )

    if len(conversation_history) > MAX_HISTORY:
        conversation_history = conversation_history[
            -MAX_HISTORY:
        ]

    save_memory(
        conversation_history
    )

    print("My AI:", response)