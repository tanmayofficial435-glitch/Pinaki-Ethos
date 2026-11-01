import torch
import torch.nn as nn


class MyAIModel(nn.Module):
    """
    Basic neural-network foundation for My AI.

    This is NOT the final language model yet.
    We will build the tokenizer, training system,
    memory, and generation system around it.
    """

    def __init__(
        self,
        vocab_size=5000,
        embedding_dim=128,
        hidden_dim=256
    ):
        super().__init__()

        self.embedding = nn.Embedding(
            vocab_size,
            embedding_dim
        )

        self.layers = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),

            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),

            nn.Linear(hidden_dim, vocab_size)
        )

    def forward(self, tokens):
        embeddings = self.embedding(tokens)

        # Combine the token representations
        x = embeddings.mean(dim=1)

        return self.layers(x)


def create_model():

    model = MyAIModel()

    parameter_count = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    print("=================================")
    print("🧠 MY AI MODEL")
    print("=================================")
    print(f"Parameters: {parameter_count:,}")
    print("Model created successfully!")
    print("=================================")

    return model


if __name__ == "__main__":
    create_model()