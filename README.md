# For ligand UMAP Analysis

A molecular feature reduction workflow for SMILES-based datasets. It supports three feature types:

- `fingerprint`: RDKit fingerprint combinations, including Morgan, MACCS, AtomPair, and Topological Torsion
- `descriptor`: RDKit molecular descriptors
- `chembert`: embeddings from pretrained ChemBERT / ChemBERTa models

Pipeline:

**Load SMILES data → parse / repair SMILES → build features → PCA denoising → UMAP reduction → KMeans clustering → export CSV files and plots**

---

## Repository Layout

```text
.
├── molecular_feature_case/
│   ├── cli.py                          # Command-line entry point
│   ├── config.py                       # Parameters and configuration
│   ├── dependencies.py                 # Runtime dependency loading
│   ├── pipeline.py                     # Main pipeline orchestration
│   ├── models/
│   │   └── chembert.py                 # ChemBERT embedding model
│   └── tools/
│       ├── clustering.py               # Cluster-number evaluation and KMeans
│       ├── descriptors.py              # RDKit descriptors
│       ├── fingerprints.py             # RDKit fingerprints
│       ├── io.py                       # Data loading and column-name detection
│       ├── plotting.py                 # Visualization output
│       ├── reduction.py                # PCA / UMAP
│       └── smiles.py                   # SMILES parsing and fallback repair
├── molecular_feature_reduction_case.py # Lightweight entry for backward compatibility
├── scripts/
│   └── demo.ipynb                      # Runnable small-sample demo
├── pyproject.toml
├── requirements.txt
├── requirements-chembert.txt
└── README.md
```

---

## Installation

Install the core environment:

```bash
pip install -r requirements.txt
```

Install ChemBERT dependencies if needed:

```bash
pip install -r requirements-chembert.txt
```

Or install the package directly:

```bash
pip install -e .
```

If `pip install rdkit` is unstable in your environment, using Conda is recommended:

```bash
conda install -c conda-forge rdkit
```

---

## Input Format

Input files support CSV and TSV.

The program automatically searches for a SMILES column using:

- `SMILES`
- `psmiles`
- `smiles_list`
- `canonical_smiles`

If none of these are found, the first column is used as the SMILES column.

For identifiers, the program searches for:

- `ID`
- `id`
- `name`
- `Name`
- `index`

If no ID column is found, row indices are generated automatically.

---

## Usage

### Notebook demo

```bash
jupyter notebook scripts/demo.ipynb
```

### RDKit fingerprints

```bash
python molecular_feature_reduction_case.py \
  --input data.csv \
  --feature-type fingerprint \
  --output-dir outputs_fingerprint
```

### RDKit descriptors

```bash
python molecular_feature_reduction_case.py \
  --input data.csv \
  --feature-type descriptor \
  --output-dir outputs_descriptor
```

### ChemBERT embeddings

```bash
python molecular_feature_reduction_case.py \
  --input data.csv \
  --feature-type chembert \
  --chembert-model seyonec/ChemBERTa-zinc-base-v1 \
  --output-dir outputs_chembert
```

After package installation, you can also run:

```bash
molecular-feature-case --input data.csv --feature-type descriptor
```

---

## Useful Options

Specify columns:

```bash
--smiles-column psmiles --id-column auto
```

Force cluster count:

```bash
--force-clusters 8
```

Tune UMAP:

```bash
--umap-components 3 --umap-neighbors 10 --umap-min-dist 0.01 --umap-metric cosine
```

Highlight selected IDs:

```bash
--ids-to-mark 224,225,226,227
```

Use Morgan fingerprint only:

```bash
--single-fingerprint
```

Load ChemBERT from local files only:

```bash
--chembert-local-files-only
```

---

## Outputs

Each run generates the following files under `--output-dir`:

- `clustered_molecules_<feature_type>.csv`: IDs, processed SMILES, cluster labels, and UMAP coordinates
- `cluster_evaluation_metrics.csv`: evaluation metrics and overall scores for different cluster counts
- `cluster_evaluation_metrics.png`: cluster evaluation plot
- `umap_<feature_type>_clusters.png`: UMAP clustering plot
- `run_metadata.json`: run parameters, sample count, feature dimension, PCA explained variance, and related metadata
- `umap_dimension_plots/`: additional dimension plots when `--umap-components > 2`

---

## Notes

- `fingerprint` is suitable for quickly reproducing the original notebook workflow.
- `descriptor` is generally easier to interpret.
- `chembert` is suitable for exploring pretrained semantic representations of SMILES, but it requires additional model files and longer runtime.
