from __future__ import annotations

from pathlib import Path


def read_table(path: Path, pd_module):
    if not path.exists():
        raise FileNotFoundError(f"Input file does not exist: {path}")

    readers = [
        {"sep": None, "engine": "python"},
        {"sep": "\t"},
        {"sep": ","},
    ]
    last_error: Exception | None = None
    for kwargs in readers:
        try:
            df = pd_module.read_csv(path, **kwargs)
            if len(df.columns) >= 1:
                return df
        except Exception as exc:  # pragma: no cover - fallback path
            last_error = exc

    raise ValueError(f"Could not read {path}: {last_error}")


def resolve_columns(df, smiles_column: str, id_column: str):
    columns_lower = {str(col).lower(): col for col in df.columns}

    if smiles_column == "auto":
        candidates = ["smiles", "psmiles", "smiles_list", "canonical_smiles"]
        source = next((columns_lower[name] for name in candidates if name in columns_lower), None)
        if source is None:
            source = df.columns[0]
    elif smiles_column in df.columns:
        source = smiles_column
    elif smiles_column.lower() in columns_lower:
        source = columns_lower[smiles_column.lower()]
    else:
        raise ValueError(
            f"SMILES column `{smiles_column}` not found. Available columns: {list(df.columns)}"
        )

    if source != "SMILES":
        df = df.rename(columns={source: "SMILES"})

    if id_column == "auto":
        id_candidates = ["id", "ID", "name", "Name", "index"]
        id_source = next((col for col in id_candidates if col in df.columns), None)
    elif id_column in df.columns:
        id_source = id_column
    elif id_column.lower() in columns_lower:
        id_source = columns_lower[id_column.lower()]
    else:
        id_source = None

    if id_source is None or id_source == "SMILES":
        df.insert(0, "ID", list(range(1, len(df) + 1)))
    elif id_source != "ID":
        df = df.rename(columns={id_source: "ID"})

    return df

