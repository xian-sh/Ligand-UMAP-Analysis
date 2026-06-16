from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RuntimeDeps:
    np: Any
    pd: Any
    plt: Any
    umap: Any
    Chem: Any
    DataStructs: Any
    RDLogger: Any
    AllChem: Any
    Descriptors: Any
    MACCSkeys: Any
    KMeans: Any
    PCA: Any
    SimpleImputer: Any
    StandardScaler: Any
    silhouette_score: Any
    davies_bouldin_score: Any
    calinski_harabasz_score: Any
    tqdm: Any


def load_runtime_deps() -> RuntimeDeps:
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt
        import numpy as np
        import pandas as pd
        import umap
        from rdkit import Chem, DataStructs, RDLogger
        from rdkit.Chem import AllChem, Descriptors, MACCSkeys
        from sklearn.cluster import KMeans
        from sklearn.decomposition import PCA
        from sklearn.impute import SimpleImputer
        from sklearn.metrics import calinski_harabasz_score
        from sklearn.metrics import davies_bouldin_score
        from sklearn.metrics import silhouette_score
        from sklearn.preprocessing import StandardScaler
        from tqdm.auto import tqdm
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency for fingerprint/descriptor workflows. Install the core stack:\n"
            "  pip install pandas numpy matplotlib scikit-learn umap-learn tqdm rdkit"
        ) from exc

    return RuntimeDeps(
        np=np,
        pd=pd,
        plt=plt,
        umap=umap,
        Chem=Chem,
        DataStructs=DataStructs,
        RDLogger=RDLogger,
        AllChem=AllChem,
        Descriptors=Descriptors,
        MACCSkeys=MACCSkeys,
        KMeans=KMeans,
        PCA=PCA,
        SimpleImputer=SimpleImputer,
        StandardScaler=StandardScaler,
        silhouette_score=silhouette_score,
        davies_bouldin_score=davies_bouldin_score,
        calinski_harabasz_score=calinski_harabasz_score,
        tqdm=tqdm,
    )

