from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


FeatureType = Literal["fingerprint", "descriptor", "chembert"]


@dataclass
class Config:
    input: Path
    output_dir: Path = Path("molecular_feature_outputs")
    smiles_column: str = "auto"
    id_column: str = "auto"
    feature_type: FeatureType = "fingerprint"
    fp_bits: int = 2048
    use_multiple_fps: bool = True
    pca_components: int = 100
    umap_components: int = 2
    umap_neighbors: int = 5
    umap_min_dist: float = 0.001
    umap_metric: str = "cosine"
    min_clusters: int = 5
    max_clusters: int = 10
    force_clusters: int | None = None
    random_state: int = 42
    ids_to_mark: tuple[str, ...] = ()
    chembert_model: str = "seyonec/ChemBERTa-zinc-base-v1"
    chembert_batch_size: int = 16
    chembert_max_length: int = 256
    chembert_local_files_only: bool = False
    chembert_pooling: Literal["cls", "mean"] = "mean"
    device: str = "auto"


def parse_args(argv: list[str] | None = None) -> Config:
    parser = argparse.ArgumentParser(
        description="Run molecular feature extraction, UMAP reduction, and KMeans clustering."
    )
    parser.add_argument("--input", required=True, type=Path, help="Input CSV/TSV file.")
    parser.add_argument("--output-dir", default=Path("molecular_feature_outputs"), type=Path)
    parser.add_argument(
        "--smiles-column",
        default="auto",
        help="SMILES column name. Default `auto` chooses SMILES, psmiles, smiles_list, or the first column.",
    )
    parser.add_argument(
        "--id-column",
        default="auto",
        help="ID column name. Default `auto` uses an ID/name column or generates row IDs.",
    )
    parser.add_argument(
        "--feature-type",
        choices=["fingerprint", "descriptor", "chembert"],
        default="fingerprint",
        help="Feature source used before dimensionality reduction.",
    )
    parser.add_argument("--fp-bits", default=2048, type=int)
    parser.add_argument(
        "--single-fingerprint",
        action="store_true",
        help="Use Morgan fingerprint only instead of Morgan+MACCS+AtomPair+Torsion.",
    )
    parser.add_argument("--pca-components", default=100, type=int)
    parser.add_argument("--umap-components", default=2, type=int)
    parser.add_argument("--umap-neighbors", default=5, type=int)
    parser.add_argument("--umap-min-dist", default=0.001, type=float)
    parser.add_argument("--umap-metric", default="cosine")
    parser.add_argument("--min-clusters", default=5, type=int)
    parser.add_argument("--max-clusters", default=10, type=int)
    parser.add_argument("--force-clusters", default=None, type=int)
    parser.add_argument("--random-state", default=42, type=int)
    parser.add_argument(
        "--ids-to-mark",
        default="",
        help="Comma-separated IDs highlighted with black X markers in scatter plots.",
    )
    parser.add_argument(
        "--chembert-model",
        default="seyonec/ChemBERTa-zinc-base-v1",
        help="Hugging Face model name or local model directory.",
    )
    parser.add_argument("--chembert-batch-size", default=16, type=int)
    parser.add_argument("--chembert-max-length", default=256, type=int)
    parser.add_argument(
        "--chembert-local-files-only",
        action="store_true",
        help="Load ChemBERT model only from the local Hugging Face cache or local path.",
    )
    parser.add_argument("--chembert-pooling", choices=["cls", "mean"], default="mean")
    parser.add_argument(
        "--device",
        default="auto",
        help="Device for ChemBERT embeddings: auto, cpu, cuda, cuda:0, etc.",
    )

    args = parser.parse_args(argv)
    marked_ids = tuple(x.strip() for x in args.ids_to_mark.split(",") if x.strip())

    return Config(
        input=args.input,
        output_dir=args.output_dir,
        smiles_column=args.smiles_column,
        id_column=args.id_column,
        feature_type=args.feature_type,
        fp_bits=args.fp_bits,
        use_multiple_fps=not args.single_fingerprint,
        pca_components=args.pca_components,
        umap_components=args.umap_components,
        umap_neighbors=args.umap_neighbors,
        umap_min_dist=args.umap_min_dist,
        umap_metric=args.umap_metric,
        min_clusters=args.min_clusters,
        max_clusters=args.max_clusters,
        force_clusters=args.force_clusters,
        random_state=args.random_state,
        ids_to_mark=marked_ids,
        chembert_model=args.chembert_model,
        chembert_batch_size=args.chembert_batch_size,
        chembert_max_length=args.chembert_max_length,
        chembert_local_files_only=args.chembert_local_files_only,
        chembert_pooling=args.chembert_pooling,
        device=args.device,
    )

