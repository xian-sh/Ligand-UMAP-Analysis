from __future__ import annotations


def build_descriptor_features(mols, deps):
    descriptor_items = list(deps.Descriptors.descList)
    descriptor_names = [name for name, _ in descriptor_items]

    rows: list[list[float]] = []
    for mol in deps.tqdm(mols, desc="Calculating RDKit descriptors"):
        values = []
        for _, func in descriptor_items:
            try:
                value = float(func(mol))
            except Exception:
                value = deps.np.nan
            if deps.np.isinf(value):
                value = deps.np.nan
            values.append(value)
        rows.append(values)

    matrix = deps.np.asarray(rows, dtype=deps.np.float32)
    keep_mask = ~deps.np.all(deps.np.isnan(matrix), axis=0)
    matrix = matrix[:, keep_mask]
    descriptor_names = [name for name, keep in zip(descriptor_names, keep_mask) if keep]

    matrix = deps.SimpleImputer(strategy="median").fit_transform(matrix)
    matrix = deps.StandardScaler().fit_transform(matrix)
    return matrix.astype(deps.np.float32), descriptor_names

