import torch
import torch.nn as nn


class MyAIModel(nn.Module):

    def __init__(
        self,
        vocab_size,
        embedding_dim=128,
        num_heads=4,
        num_layers=2,
        max_sequence_length=64
    ):
        super().__init__()

        self.max_sequence_length = max_sequence_length

        # Token embeddings
        self.token_embedding = nn.Embedding(
            vocab_size,
            embedding_dim
        )

        # Position embeddings
        self.position_embedding = nn.Embedding(
            max_sequence_length,
            embedding_dim
        )

        # Transformer
        transformer_layer = nn.TransformerEncoderLayer(
            d_model=embedding_dim,
            nhead=num_heads,
            dim_feedforward=256,
            dropout=0.1,
            batch_first=True
        )

        self.transformer = nn.TransformerEncoder(
            transformer_layer,
            num_layers=num_layers
        )

        # Convert hidden states into vocabulary predictions
        self.output_layer = nn.Linear(
            embedding_dim,
            vocab_size
        )

    def forward(self, tokens):

        batch_size, sequence_length = tokens.shape

        # Prevent sequences from becoming too long
        if sequence_length > self.max_sequence_length:
            tokens = tokens[:, -self.max_sequence_length:]
            sequence_length = self.max_sequence_length

        positions = torch.arange(
            sequence_length,
            device=tokens.device
        ).unsqueeze(0)

        token_embeddings = self.token_embedding(tokens)
        position_embeddings = self.position_embedding(positions)

        x = token_embeddings + position_embeddings

        # Causal mask:
        # each token can only look at previous tokens
        mask = torch.triu(
            torch.ones(
                sequence_length,
                sequence_length,
                device=tokens.device
            ),
            diagonal=1
        ).bool()

        x = self.transformer(
            x,
            mask=mask
        )

        logits = self.output_layer(x)

        return logits


def create_model(vocab_size=5000):

    model = MyAIModel(
        vocab_size=vocab_size
    )

    parameter_count = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    print("=================================")
    print("🧠 MY AI TRANSFORMER")
    print("=================================")
    print(f"Parameters: {parameter_count:,}")
    print("Model created successfully!")
    print("=================================")

    return model


if __name__ == "__main__":

    create_model()