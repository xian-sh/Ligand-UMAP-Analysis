from __future__ import annotations


def bitvect_to_array(bitvect, deps, length: int):
    arr = deps.np.zeros((length,), dtype=deps.np.float32)
    deps.DataStructs.ConvertToNumpyArray(bitvect, arr)
    return arr


def calculate_fingerprint(mol, cfg, deps):
    morgan = deps.AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=cfg.fp_bits)
    morgan_arr = bitvect_to_array(morgan, deps, cfg.fp_bits)

    if not cfg.use_multiple_fps:
        return morgan_arr

    atom_pair = deps.AllChem.GetHashedAtomPairFingerprintAsBitVect(mol, nBits=cfg.fp_bits)
    torsion = deps.AllChem.GetHashedTopologicalTorsionFingerprintAsBitVect(mol, nBits=cfg.fp_bits)
    maccs = deps.MACCSkeys.GenMACCSKeys(mol)

    atom_pair_arr = bitvect_to_array(atom_pair, deps, cfg.fp_bits)
    torsion_arr = bitvect_to_array(torsion, deps, cfg.fp_bits)
    maccs_arr = deps.np.zeros((cfg.fp_bits,), dtype=deps.np.float32)
    maccs_raw = deps.np.zeros((167,), dtype=deps.np.float32)
    deps.DataStructs.ConvertToNumpyArray(maccs, maccs_raw)
    maccs_arr[:167] = maccs_raw

    return (
        0.50 * morgan_arr
        + 0.20 * atom_pair_arr
        + 0.15 * torsion_arr
        + 0.15 * maccs_arr
    )


def build_fingerprint_features(mols, cfg, deps):
    features = [
        calculate_fingerprint(mol, cfg, deps)
        for mol in deps.tqdm(mols, desc="Calculating fingerprints")
    ]
    names = [f"fp_{i}" for i in range(cfg.fp_bits)]
    return deps.np.asarray(features, dtype=deps.np.float32), names

