import re
import json
from pathlib import Path


class MyAITokenizer:

    def __init__(self):

        self.token_to_id = {
            "<PAD>": 0,
            "<UNK>": 1,
            "<BOS>": 2,
            "<EOS>": 3,
            "<SEP>": 4
        }

        self.id_to_token = {
            0: "<PAD>",
            1: "<UNK>",
            2: "<BOS>",
            3: "<EOS>",
            4: "<SEP>"
        }

    def split_text(self, text):

        # Recognize special tokens regardless of capitalization
        pattern = r"<BOS>|<EOS>|<SEP>|<PAD>|<UNK>|\w+|[^\w\s]"

        return re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

    def build_vocabulary(self, text):

        tokens = self.split_text(text)

        for token in tokens:

            token = token.upper() if token.startswith("<") else token.lower()

            if token not in self.token_to_id:

                token_id = len(self.token_to_id)

                self.token_to_id[token] = token_id
                self.id_to_token[token_id] = token

    def encode(self, text):

        tokens = self.split_text(text)

        converted = []

        for token in tokens:

            if token.startswith("<") and token.endswith(">"):
                token = token.upper()
            else:
                token = token.lower()

            converted.append(
                self.token_to_id.get(
                    token,
                    self.token_to_id["<UNK>"]
                )
            )

        return converted

    def decode(self, token_ids):

        tokens = []

        for token_id in token_ids:

            token = self.id_to_token.get(
                token_id,
                "<UNK>"
            )

            # Hide control tokens
            if token in {
                "<PAD>",
                "<BOS>",
                "<EOS>",
                "<SEP>"
            }:
                continue

            tokens.append(token)

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
            json.dumps(
                data,
                indent=2
            ),
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

    sample_text = "<BOS> Hello! <SEP> I am My AI. <EOS>"

    tokenizer.build_vocabulary(sample_text)

    encoded = tokenizer.encode(sample_text)
    decoded = tokenizer.decode(encoded)

    print("=================================")
    print("🧠 MY AI TOKENIZER")
    print("=================================")
    print("Vocabulary size:", len(tokenizer.token_to_id))
    print("Encoded:", encoded)
    print("Decoded:", decoded)
    print("Special tokens:")

    print("BOS:", tokenizer.token_to_id["<BOS>"])
    print("SEP:", tokenizer.token_to_id["<SEP>"])
    print("EOS:", tokenizer.token_to_id["<EOS>"])

    print("=================================")