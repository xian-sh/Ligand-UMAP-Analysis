from __future__ import annotations

import json
import random
import warnings
from dataclasses import asdict
from pathlib import Path

from .config import Config
from .dependencies import RuntimeDeps, load_runtime_deps
from .models import build_chembert_features
from .tools import (
    build_descriptor_features,
    build_fingerprint_features,
    evaluate_cluster_counts,
    fit_clusters,
    force_process_smiles,
    preprocess_for_umap,
    read_table,
    resolve_columns,
    run_umap,
    save_embedding_plots,
    save_metric_plot,
)


def configure_runtime(seed: int, deps: RuntimeDeps) -> None:
    warnings.filterwarnings("ignore")
    deps.RDLogger.DisableLog("rdApp.*")
    random.seed(seed)
    deps.np.random.seed(seed)


def build_features(cfg: Config, mols, processed_smiles, deps: RuntimeDeps):
    if cfg.feature_type == "fingerprint":
        return build_fingerprint_features(mols, cfg, deps)
    if cfg.feature_type == "descriptor":
        return build_descriptor_features(mols, deps)
    if cfg.feature_type == "chembert":
        return build_chembert_features(processed_smiles, cfg)
    raise ValueError(f"Unsupported feature type: {cfg.feature_type}")


def save_outputs(
    df,
    processed_smiles,
    valid_smiles,
    embedding,
    labels,
    metrics,
    selected_clusters: int,
    feature_names: list[str],
    pca_info: dict[str, float],
    cfg: Config,
    deps: RuntimeDeps,
) -> None:
    cfg.output_dir.mkdir(parents=True, exist_ok=True)

    result = deps.pd.DataFrame(
        {
            "ID": df["ID"].tolist(),
            "SMILES": processed_smiles,
            "SMILES_valid_or_repaired": valid_smiles,
            "feature_type": cfg.feature_type,
            "Cluster": labels,
        }
    )
    for dim in range(embedding.shape[1]):
        result[f"UMAP{dim + 1}"] = embedding[:, dim]
    result.to_csv(cfg.output_dir / f"clustered_molecules_{cfg.feature_type}.csv", index=False)

    if metrics:
        deps.pd.DataFrame(asdict(metric) for metric in metrics).to_csv(
            cfg.output_dir / "cluster_evaluation_metrics.csv", index=False
        )

    metadata = {
        "config": {
            key: str(value) if isinstance(value, Path) else value
            for key, value in asdict(cfg).items()
        },
        "selected_clusters": selected_clusters,
        "n_samples": int(len(df)),
        "n_features": int(len(feature_names)),
        "first_feature_names": feature_names[:20],
        **pca_info,
    }
    with open(cfg.output_dir / "run_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def run_pipeline(cfg: Config) -> None:
    deps = load_runtime_deps()
    configure_runtime(cfg.random_state, deps)
    cfg.output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Reading data from {cfg.input}")
    df = read_table(cfg.input, deps.pd)
    df = resolve_columns(df, cfg.smiles_column, cfg.id_column)
    print(f"Loaded {len(df)} rows")

    mols = []
    processed_smiles = []
    valid_smiles = []
    for smiles in deps.tqdm(df["SMILES"].tolist(), desc="Parsing SMILES"):
        mol, fixed_smiles, ok = force_process_smiles(smiles, deps.Chem)
        mols.append(mol)
        processed_smiles.append(fixed_smiles)
        valid_smiles.append(ok)

    print(f"Building {cfg.feature_type} features")
    features, feature_names = build_features(cfg, mols, processed_smiles, deps)
    print(f"Feature matrix: {features.shape[0]} samples x {features.shape[1]} features")

    print("Running PCA pre-processing")
    features_for_umap, pca_info = preprocess_for_umap(features, cfg, deps)
    print(
        f"PCA components={int(pca_info['pca_components'])}, "
        f"explained variance={pca_info['pca_explained_variance']:.4f}"
    )

    print("Running UMAP")
    embedding = run_umap(features_for_umap, cfg, deps)

    print("Selecting cluster count")
    selected_clusters, metrics = evaluate_cluster_counts(embedding, cfg, deps)
    print(f"Selected clusters: {selected_clusters}")

    print("Running KMeans")
    labels = fit_clusters(embedding, selected_clusters, deps, cfg.random_state)

    save_outputs(
        df=df,
        processed_smiles=processed_smiles,
        valid_smiles=valid_smiles,
        embedding=embedding,
        labels=labels,
        metrics=metrics,
        selected_clusters=selected_clusters,
        feature_names=feature_names,
        pca_info=pca_info,
        cfg=cfg,
        deps=deps,
    )
    save_metric_plot(metrics, selected_clusters, cfg.output_dir, deps)
    save_embedding_plots(embedding, labels, df["ID"].tolist(), cfg, deps)

    counts = deps.pd.Series(labels).value_counts().sort_index()
    print("Cluster counts:")
    for cluster_id, count in counts.items():
        print(f"  Cluster {cluster_id}: {count}")
    print(f"Done. Results saved to {cfg.output_dir}")

