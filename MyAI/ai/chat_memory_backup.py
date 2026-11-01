import torch

from model import MyAIModel
from tokenizer import MyAITokenizer


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
# CONVERSATION MEMORY
# =================================

conversation_history = []

MAX_HISTORY = 3


# =================================
# GENERATE RESPONSE
# =================================

def generate_response(prompt, max_tokens=40):

    # Build recent conversation context
    context_parts = []

    for user_message, ai_message in conversation_history[-MAX_HISTORY:]:
        context_parts.append(
            "<BOS> "
            + user_message
            + " <SEP> "
            + ai_message
            + " <EOS>"
        )

    # Add the current question
    context_parts.append(
        "<BOS> "
        + prompt
        + " <SEP>"
    )

    full_prompt = " ".join(context_parts)

    prompt_tokens = tokenizer.encode(full_prompt)

    generated = prompt_tokens.copy()

    for _ in range(max_tokens):

        # The model was trained with short sequences
        input_tokens = generated[-16:]

        input_tensor = torch.tensor(
            [input_tokens],
            dtype=torch.long
        )

        with torch.no_grad():
            output = model(input_tensor)

        logits = output[0, -1]

        next_token = torch.argmax(logits).item()

        generated.append(next_token)

        if next_token == EOS_ID:
            break

    # Tokens generated after the current <SEP>
    current_prompt_tokens = tokenizer.encode(
        "<BOS> " + prompt + " <SEP>"
    )

    response_tokens = generated[
        len(generated) - (len(generated) - len(prompt_tokens)):
    ]

    # Find the final EOS boundary
    new_tokens = generated[len(prompt_tokens):]

    if EOS_ID in new_tokens:
        new_tokens = new_tokens[
            :new_tokens.index(EOS_ID)
        ]

    response = tokenizer.decode(new_tokens).strip()

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
print("Short-term conversation memory enabled.")
print("Type 'exit' to stop.")
print("Type 'clear' to clear memory.")
print("=================================")
print()


while True:

    user_input = input("You: ").strip()

    if not user_input:
        continue

    if user_input.lower() == "exit":
        print("My AI: Goodbye! 👋")
        break

    if user_input.lower() == "clear":
        conversation_history.clear()
        print("My AI: Conversation memory cleared. 🧹")
        continue

    response = generate_response(user_input)

    conversation_history.append(
        (user_input, response)
    )

    # Keep only recent conversations
    if len(conversation_history) > MAX_HISTORY:
        conversation_history.pop(0)

    print("My AI:", response)