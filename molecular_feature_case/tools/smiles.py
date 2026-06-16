from __future__ import annotations


def _is_missing(value) -> bool:
    try:
        return value is None or value != value
    except Exception:
        return False


def force_process_smiles(smiles, Chem):
    raw = "" if _is_missing(smiles) else str(smiles).strip()
    if not raw:
        return Chem.MolFromSmiles("CC"), "CC", False

    attempts = [raw]

    open_count = raw.count("(")
    close_count = raw.count(")")
    if open_count != close_count:
        if open_count > close_count:
            attempts.append(raw + ")" * (open_count - close_count))
        else:
            attempts.append(raw.replace(")", "", close_count - open_count))

    attempts.append(raw.replace("%", "*").replace("$", "*").replace("?", "*").replace("~", "*"))
    attempts.append(raw.replace("c", "C").replace("n", "N"))
    attempts.extend(part for part in raw.split(".") if part)

    seen: set[str] = set()
    for candidate in attempts:
        if candidate in seen:
            continue
        seen.add(candidate)
        try:
            mol = Chem.MolFromSmiles(candidate)
            if mol is not None:
                return mol, Chem.MolToSmiles(mol, canonical=True), True
        except Exception:
            continue

    return Chem.MolFromSmiles("CC"), "CC", False

