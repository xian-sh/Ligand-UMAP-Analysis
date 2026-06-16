from __future__ import annotations


def choose_torch_device(requested: str):
    import torch

    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(requested)


def masked_mean_pooling(hidden_states, attention_mask):
    import torch

    mask = attention_mask.unsqueeze(-1).expand(hidden_states.size()).float()
    summed = torch.sum(hidden_states * mask, dim=1)
    counts = torch.clamp(mask.sum(dim=1), min=1e-9)
    return summed / counts


def build_chembert_features(smiles, cfg):
    try:
        import numpy as np
        import torch
        from transformers import AutoModel, AutoTokenizer
    except ImportError as exc:
        raise SystemExit(
            "ChemBERT mode requires torch and transformers. Install them with `pip install torch transformers`."
        ) from exc

    device = choose_torch_device(cfg.device)
    tokenizer = AutoTokenizer.from_pretrained(
        cfg.chembert_model, local_files_only=cfg.chembert_local_files_only
    )
    model = AutoModel.from_pretrained(
        cfg.chembert_model, local_files_only=cfg.chembert_local_files_only
    )
    model.to(device)
    model.eval()

    embeddings: list[np.ndarray] = []
    for start in range(0, len(smiles), cfg.chembert_batch_size):
        batch = smiles[start : start + cfg.chembert_batch_size]
        encoded = tokenizer(
            batch,
            padding=True,
            truncation=True,
            max_length=cfg.chembert_max_length,
            return_tensors="pt",
        )
        encoded = {key: value.to(device) for key, value in encoded.items()}

        with torch.no_grad():
            outputs = model(**encoded)
            hidden = outputs.last_hidden_state
            if cfg.chembert_pooling == "cls":
                pooled = hidden[:, 0, :]
            else:
                pooled = masked_mean_pooling(hidden, encoded["attention_mask"])

        embeddings.append(pooled.detach().cpu().numpy())

    matrix = np.vstack(embeddings).astype(np.float32)
    names = [f"chembert_{i}" for i in range(matrix.shape[1])]
    return matrix, names

