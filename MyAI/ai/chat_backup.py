import torch

from model import MyAIModel
from tokenizer import MyAITokenizer


# ==============================
# LOAD TOKENIZER
# ==============================

tokenizer = MyAITokenizer()
tokenizer.load("ai/tokenizer.json")

vocab_size = len(tokenizer.token_to_id)


# ==============================
# LOAD MODEL
# ==============================

model = MyAIModel(vocab_size=vocab_size)

model.load_state_dict(
    torch.load(
        "ai/my_ai_model.pth",
        map_location="cpu"
    )
)

model.eval()


# ==============================
# GENERATE RESPONSE
# ==============================

def generate_response(prompt, max_tokens=15):

    tokens = tokenizer.encode(prompt)

    if not tokens:
        return "Please say something."

    generated = tokens.copy()

    for _ in range(max_tokens):

        # Keep the most recent tokens
        input_tokens = generated[-4:]

        input_tensor = torch.tensor(
            [input_tokens],
            dtype=torch.long
        )

        with torch.no_grad():
            output = model(input_tensor)

        next_token = torch.argmax(
            output,
            dim=-1
        ).item()

        generated.append(next_token)

        # Stop at EOS
        if next_token == tokenizer.token_to_id.get("<EOS>"):
            break

    # Only return newly generated tokens
    new_tokens = generated[len(tokens):]

    if not new_tokens:
        return "I'm still learning."

    return tokenizer.decode(new_tokens)


# ==============================
# CHAT
# ==============================

print("=================================")
print("🧠 MY AI")
print("=================================")
print("Local AI model loaded successfully.")
print("Type 'exit' to stop.")
print("=================================")
print()


while True:

    user_input = input("You: ").strip()

    if user_input.lower() == "exit":

        print("My AI: Goodbye! 👋")
        break

    response = generate_response(user_input)

    print("My AI:", response)