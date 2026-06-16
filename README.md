# Molecular Feature Case

A molecular feature reduction workflow for **SMILES-based datasets**. It supports three feature types:

- `fingerprint`: combined RDKit fingerprints, including Morgan, MACCS, AtomPair, and Topological Torsion
- `descriptor`: RDKit molecular descriptors
- `chembert`: embeddings from pretrained ChemBERT / ChemBERTa models

The overall pipeline is:

**Load SMILES data → parse / repair SMILES → build features → PCA denoising → UMAP dimensionality reduction → KMeans clustering → export CSV files and plots**

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

Installation

Install the core environment:
bash

pip install -r requirements.txt

If you want to use ChemBERT embeddings:
bash

pip install -r requirements-chembert.txt

You can also install the project as a package:
bash

pip install -e .

If pip install rdkit is unstable in your environment, using Conda is recommended:
bash

conda install -c conda-forge rdkit

Input Format

Input files support CSV and TSV formats.

By default, the program will automatically search for one of the following SMILES column names:

    SMILES
    psmiles
    smiles_list
    canonical_smiles

If none of these columns is found, the first column will be used as the SMILES column.

For molecule identifiers, the program will look for:

    ID
    id
    name
    Name
    index

If no ID column is found, row indices will be generated automatically.
Usage
Notebook demo
bash

jupyter notebook scripts/demo.ipynb

Use RDKit fingerprints
bash

python molecular_feature_reduction_case.py \
  --input data.csv \
  --feature-type fingerprint \
  --output-dir outputs_fingerprint

Use RDKit descriptors
bash

python molecular_feature_reduction_case.py \
  --input data.csv \
  --feature-type descriptor \
  --output-dir outputs_descriptor

Use ChemBERT embeddings
bash

python molecular_feature_reduction_case.py \
  --input data.csv \
  --feature-type chembert \
  --chembert-model seyonec/ChemBERTa-zinc-base-v1 \
  --output-dir outputs_chembert

After package installation, you can also run it via:
bash

molecular-feature-case --input data.csv --feature-type descriptor

Useful Options
Specify column names
bash

--smiles-column psmiles --id-column auto

Force the number of clusters
bash

--force-clusters 8

Tune UMAP parameters
bash

--umap-components 3 --umap-neighbors 10 --umap-min-dist 0.01 --umap-metric cosine

Highlight specific IDs
bash

--ids-to-mark 224,225,226,227

Use Morgan fingerprint only
bash

--single-fingerprint

Load ChemBERT from local files only
bash

--chembert-local-files-only

Outputs

Each run generates the following files under --output-dir:

    clustered_molecules_<feature_type>.csv: IDs, processed SMILES, cluster labels, and UMAP coordinates
    cluster_evaluation_metrics.csv: evaluation metrics and overall scores for different cluster counts
    cluster_evaluation_metrics.png: cluster evaluation plot
    umap_<feature_type>_clusters.png: UMAP clustering plot
    run_metadata.json: run parameters, sample count, feature dimension, PCA explained variance, and related metadata
    umap_dimension_plots/: additional dimension plots when --umap-components > 2

Notes

    fingerprint is suitable for quickly reproducing the original notebook workflow.
    descriptor is generally easier to interpret.
    chembert is better suited for exploring pretrained semantic representations of SMILES, but it requires additional model files and longer runtime.
