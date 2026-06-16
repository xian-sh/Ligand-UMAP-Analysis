# Molecular Feature Case

一个把 `Untitled1(1).ipynb` 整理成 GitHub 仓库风格的分子特征降维案例。原 notebook 只做分子指纹降维；这里拆成了可复用包结构，并支持三类特征：

- `fingerprint`：RDKit Morgan/MACCS/AtomPair/Torsion 指纹组合
- `descriptor`：RDKit 分子描述符
- `chembert`：ChemBERT/ChemBERTa 预训练模型 embedding

流程是：读取 SMILES 数据 -> 解析/修复 SMILES -> 构建特征 -> PCA 预降噪 -> UMAP 降维 -> KMeans 聚类 -> 输出 CSV 和图片。

## Repository Layout

```text
.
├── molecular_feature_case/
│   ├── cli.py                  # 命令行入口
│   ├── config.py               # 参数和配置
│   ├── dependencies.py         # 运行时依赖加载
│   ├── pipeline.py             # 主流程编排
│   ├── models/
│   │   └── chembert.py         # ChemBERT embedding 模型
│   └── tools/
│       ├── clustering.py       # 聚类数评估和 KMeans
│       ├── descriptors.py      # RDKit 描述符
│       ├── fingerprints.py     # RDKit 指纹
│       ├── io.py               # 数据读取和列名识别
│       ├── plotting.py         # 可视化输出
│       ├── reduction.py        # PCA / UMAP
│       └── smiles.py           # SMILES 解析和兜底修复
├── molecular_feature_reduction_case.py  # 兼容旧用法的轻量入口
├── scripts/
│   └── demo.ipynb           # 可直接运行的小样本 demo
├── pyproject.toml
├── requirements.txt
├── requirements-chembert.txt
└── README.md
```

## Install

核心环境：

```bash
pip install -r requirements.txt
```

如果要使用 ChemBERT：

```bash
pip install -r requirements-chembert.txt
```

也可以按包安装：

```bash
pip install -e .
```

如果 `pip install rdkit` 在你的环境里不稳定，推荐：

```bash
conda install -c conda-forge rdkit
```

## Input Format

输入文件支持 CSV/TSV。默认自动寻找这些 SMILES 列名：

- `SMILES`
- `psmiles`
- `smiles_list`
- `canonical_smiles`

如果找不到，会使用第一列作为 SMILES。ID 列默认寻找 `ID/id/name/Name/index`，找不到时自动生成行号。

## Usage

Notebook demo:

```bash
jupyter notebook scripts/demo.ipynb
```

使用 RDKit 指纹：

```bash
python molecular_feature_reduction_case.py ^
  --input polytab/PloyTab/data/calculated_polymer_data.csv ^
  --feature-type fingerprint ^
  --output-dir outputs_fingerprint
```

使用 RDKit 描述符：

```bash
python molecular_feature_reduction_case.py ^
  --input polytab/PloyTab/data/calculated_polymer_data.csv ^
  --feature-type descriptor ^
  --output-dir outputs_descriptor
```

使用 ChemBERT embedding：

```bash
python molecular_feature_reduction_case.py ^
  --input polytab/PloyTab/data/calculated_polymer_data.csv ^
  --feature-type chembert ^
  --chembert-model seyonec/ChemBERTa-zinc-base-v1 ^
  --output-dir outputs_chembert
```

安装成包以后，也可以用命令：

```bash
molecular-feature-case --input data.csv --feature-type descriptor
```

## Useful Options

指定列名：

```bash
--smiles-column psmiles --id-column auto
```

强制聚类数量：

```bash
--force-clusters 8
```

调整 UMAP：

```bash
--umap-components 3 --umap-neighbors 10 --umap-min-dist 0.01 --umap-metric cosine
```

标记指定 ID：

```bash
--ids-to-mark 224,225,226,227
```

只用 Morgan 指纹：

```bash
--single-fingerprint
```

本地加载 ChemBERT 模型：

```bash
--chembert-local-files-only
```

## Outputs

每次运行会在 `--output-dir` 下生成：

- `clustered_molecules_<feature_type>.csv`：ID、处理后的 SMILES、聚类标签、UMAP 坐标
- `cluster_evaluation_metrics.csv`：不同聚类数的评估指标和综合分数
- `cluster_evaluation_metrics.png`：聚类数评估图
- `umap_<feature_type>_clusters.png`：UMAP 聚类图
- `run_metadata.json`：运行参数、样本数、特征维度、PCA 解释方差等
- `umap_dimension_plots/`：当 `--umap-components > 2` 时输出更多维度图

## Notes

`fingerprint` 适合快速复现原 notebook；`descriptor` 更容易解释；`chembert` 更适合探索 SMILES 的预训练语义表示，但需要额外模型文件和更长运行时间。
