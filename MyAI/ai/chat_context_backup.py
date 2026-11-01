import torch

from model import MyAIModel
from tokenizer import MyAITokenizer


# =================================
# LOAD TOKENIZER
# =================================

tokenizer = MyAITokenizer()
tokenizer.load("ai/tokenizer.json")

vocab_size = len(tokenizer.token_to_id)

EOS_ID = tokenizer.token_to_id.get("<EOS>")


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
# GENERATE RESPONSE
# =================================

def generate_response(prompt, max_tokens=40):

    # Start a new conversation
    prompt_tokens = tokenizer.encode(
        "<BOS> " + prompt + " <SEP>"
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

        # Prediction for the final position
        logits = output[0, -1]

        next_token = torch.argmax(
            logits
        ).item()

        generated.append(next_token)

        # Stop when the model says EOS
        if next_token == EOS_ID:
            break

    # Remove prompt tokens
    response_tokens = generated[
        len(prompt_tokens):
    ]

    # Remove EOS if present
    response_tokens = [
        token
        for token in response_tokens
        if token != EOS_ID
    ]

    if not response_tokens:
        return "I'm still learning."

    return tokenizer.decode(
        response_tokens
    )


# =================================
# CHAT
# =================================

print("=================================")
print("🧠 MY AI")
print("=================================")
print("Local Transformer loaded.")
print("Conversation model ready.")
print("Type 'exit' to stop.")
print("=================================")
print()


while True:

    user_input = input(
        "You: "
    ).strip()

    if user_input.lower() == "exit":

        print(
            "My AI: Goodbye! 👋"
        )

        break

    if not user_input:
        continue

    response = generate_response(
        user_input
    )

    print(
        "My AI:",
        response
    )