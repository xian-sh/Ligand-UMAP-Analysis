```markdown
# Molecular Feature Case

A molecular feature reduction pipeline supporting three feature types:

- `fingerprint`: Combined RDKit Morgan/MACCS/AtomPair/Torsion fingerprints
- `descriptor`: RDKit molecular descriptors
- `chembert`: ChemBERT/ChemBERTa pre-trained model embeddings

The workflow: read SMILES data → parse/repair SMILES → build features → PCA pre-denoising → UMAP dimensionality reduction → KMeans clustering → output CSV and figures.

## Repository Layout

```text
.
├── molecular_feature_case/
│   ├── cli.py                  # Command-line entry point
│   ├── config.py               # Parameters and configuration
│   ├── dependencies.py         # Runtime dependency loading
│   ├── pipeline.py             # Main workflow orchestration
│   ├── models/
│   │   └── chembert.py         # ChemBERT embedding model
│   └── tools/
│       ├── clustering.py       # Cluster number evaluation and KMeans
│       ├── descriptors.py      # RDKit descriptors
│       ├── fingerprints.py     # RDKit fingerprints
│       ├── io.py               # Data reading and column name detection
│       ├── plotting.py         # Visualization output
│       ├── reduction.py        # PCA / UMAP
│       └── smiles.py           # SMILES parsing and fallback repair
├── molecular_feature_reduction_case.py  # Lightweight entry point for legacy usage
├── scripts/
│   └── demo.ipynb              # Ready-to-run small-sample demo
├── pyproject.toml
├── requirements.txt
├── requirements-chembert.txt
└── README.md
```

## Install

Core environment:

```bash
pip install -r requirements.txt
```

To use ChemBERT:

```bash
pip install -r requirements-chembert.txt
```

You can also install as a package:

```bash
pip install -e .
```

If `pip install rdkit` is unstable in your environment, it is recommended to use:

```bash
conda install -c conda-forge rdkit
```

## Input Format

The input file supports CSV/TSV. The following SMILES column names are automatically detected:

- `SMILES`
- `psmiles`
- `smiles_list`
- `canonical_smiles`

If none are found, the first column is used as SMILES. For ID columns, the default search includes `ID/id/name/Name/index`; if not found, row numbers are auto-generated.

## Usage

Notebook demo:

```bash
jupyter notebook scripts/demo.ipynb
```

Using RDKit fingerprints:

```bash
python molecular_feature_reduction_case.py ^
  --input polytab/PloyTab/data/calculated_polymer_data.csv ^
  --feature-type fingerprint ^
  --output-dir outputs_fingerprint
```

Using RDKit descriptors:

```bash
python molecular_feature_reduction_case.py ^
  --input polytab/PloyTab/data/calculated_polymer_data.csv ^
  --feature-type descriptor ^
  --output-dir outputs_descriptor
```

Using ChemBERT embeddings:

```bash
python molecular_feature_reduction_case.py ^
  --input polytab/PloyTab/data/calculated_polymer_data.csv ^
  --feature-type chembert ^
  --chembert-model seyonec/ChemBERTa-zinc-base-v1 ^
  --output-dir outputs_chembert
```

After installing as a package, you can also use the command:

```bash
molecular-feature-case --input data.csv --feature-type descriptor
```

## Useful Options

Specify column names:

```bash
--smiles-column psmiles --id-column auto
```

Force the number of clusters:

```bash
--force-clusters 8
```

Adjust UMAP parameters:

```bash
--umap-components 3 --umap-neighbors 10 --umap-min-dist 0.01 --umap-metric cosine
```

Mark specific IDs:

```bash
--ids-to-mark 224,225,226,227
```

Use only Morgan fingerprints:

```bash
--single-fingerprint
```

Load ChemBERT model locally:

```bash
--chembert-local-files-only
```

## Outputs

Each run generates the following files in `--output-dir`:

- `clustered_molecules_<feature_type>.csv`: ID, processed SMILES, cluster labels, UMAP coordinates
- `cluster_evaluation_metrics.csv`: Evaluation metrics and composite scores for different cluster numbers
- `cluster_evaluation_metrics.png`: Cluster number evaluation plot
- `umap_<feature_type>_clusters.png`: UMAP cluster visualization
- `run_metadata.json`: Runtime parameters, sample count, feature dimensions, PCA explained variance, etc.
- `umap_dimension_plots/`: Additional dimension plots when `--umap-components > 2`

## Notes

`fingerprint` is suitable for quickly reproducing the original notebook; `descriptor` is more interpretable; `chembert` is better suited for exploring pre-trained semantic representations of SMILES, but requires additional model files and longer runtime.
```
