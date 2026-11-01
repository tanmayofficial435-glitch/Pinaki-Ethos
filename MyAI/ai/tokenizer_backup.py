import re
import json
from pathlib import Path


class MyAITokenizer:

    def __init__(self):
        self.token_to_id = {
            "<PAD>": 0,
            "<UNK>": 1,
            "<BOS>": 2,
            "<EOS>": 3
        }

        self.id_to_token = {
            0: "<PAD>",
            1: "<UNK>",
            2: "<BOS>",
            3: "<EOS>"
        }

    def split_text(self, text):
        """
        Break text into simple words and punctuation.
        """

        return re.findall(
            r"\w+|[^\w\s]",
            text.lower()
        )

    def build_vocabulary(self, text):

        tokens = self.split_text(text)

        for token in tokens:

            if token not in self.token_to_id:

                token_id = len(self.token_to_id)

                self.token_to_id[token] = token_id
                self.id_to_token[token_id] = token

    def encode(self, text):

        tokens = self.split_text(text)

        return [
            self.token_to_id.get(token, 1)
            for token in tokens
        ]

    def decode(self, token_ids):

        tokens = [
            self.id_to_token.get(
                token_id,
                "<UNK>"
            )
            for token_id in token_ids
        ]

        return " ".join(tokens)

    def save(self, path):

        data = {
            "token_to_id": self.token_to_id,
            "id_to_token": {
                str(k): v
                for k, v in self.id_to_token.items()
            }
        }

        Path(path).write_text(
            json.dumps(data, indent=2),
            encoding="utf-8"
        )

    def load(self, path):

        data = json.loads(
            Path(path).read_text(
                encoding="utf-8"
            )
        )

        self.token_to_id = data["token_to_id"]

        self.id_to_token = {
            int(k): v
            for k, v in data["id_to_token"].items()
        }


if __name__ == "__main__":

    tokenizer = MyAITokenizer()

    sample_text = """
    Hello! I am My AI.
    I can have conversations.
    I can help people create ideas.
    """

    tokenizer.build_vocabulary(sample_text)

    encoded = tokenizer.encode(
        "Hello My AI"
    )

    decoded = tokenizer.decode(
        encoded
    )

    print("=================================")
    print("🧠 MY AI TOKENIZER")
    print("=================================")

    print("Vocabulary size:",
          len(tokenizer.token_to_id))

    print("Encoded:",
          encoded)

    print("Decoded:",
          decoded)

    print("=================================")