from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClusterMetric:
    n_clusters: int
    silhouette: float
    davies_bouldin: float
    calinski_harabasz: float
    combined_score: float


def normalize(values, deps, higher_is_better: bool = True):
    vals = deps.np.asarray(list(values), dtype=deps.np.float64)
    finite = deps.np.isfinite(vals)
    if not finite.any():
        return [0.0 for _ in vals]

    min_val = vals[finite].min()
    max_val = vals[finite].max()
    denom = max(max_val - min_val, 1e-10)
    norm = (vals - min_val) / denom
    if not higher_is_better:
        norm = 1.0 - norm
    norm[~finite] = 0.0
    return norm.tolist()


def evaluate_cluster_counts(embedding, cfg, deps):
    n_samples = len(embedding)
    if cfg.force_clusters is not None:
        return cfg.force_clusters, []

    min_clusters = max(2, cfg.min_clusters)
    max_by_samples = max(2, n_samples - 1)
    max_by_rule = max(2, int(deps.np.sqrt(n_samples) * 1.5))
    max_clusters = min(cfg.max_clusters, max_by_samples, max_by_rule)
    if max_clusters < min_clusters:
        min_clusters = 2
        max_clusters = min(max_clusters, max_by_samples)

    raw_rows = []
    for n_clusters in range(min_clusters, max_clusters + 1):
        try:
            labels = deps.KMeans(
                n_clusters=n_clusters,
                random_state=cfg.random_state,
                n_init=10,
            ).fit_predict(embedding)
            raw_rows.append(
                {
                    "n_clusters": n_clusters,
                    "silhouette": deps.silhouette_score(embedding, labels),
                    "davies_bouldin": deps.davies_bouldin_score(embedding, labels),
                    "calinski_harabasz": deps.calinski_harabasz_score(embedding, labels),
                }
            )
        except Exception:
            raw_rows.append(
                {
                    "n_clusters": n_clusters,
                    "silhouette": -1.0,
                    "davies_bouldin": deps.np.inf,
                    "calinski_harabasz": -1.0,
                }
            )

    sil_norm = normalize((row["silhouette"] for row in raw_rows), deps, higher_is_better=True)
    db_norm = normalize((row["davies_bouldin"] for row in raw_rows), deps, higher_is_better=False)
    ch_norm = normalize((row["calinski_harabasz"] for row in raw_rows), deps, higher_is_better=True)

    metrics: list[ClusterMetric] = []
    for idx, row in enumerate(raw_rows):
        cluster_bias = 0.05 * idx
        combined = 0.4 * sil_norm[idx] + 0.3 * db_norm[idx] + 0.3 * ch_norm[idx] + cluster_bias
        metrics.append(
            ClusterMetric(
                n_clusters=int(row["n_clusters"]),
                silhouette=float(row["silhouette"]),
                davies_bouldin=float(row["davies_bouldin"]),
                calinski_harabasz=float(row["calinski_harabasz"]),
                combined_score=float(combined),
            )
        )

    if not metrics:
        return 2, metrics

    best = max(metrics, key=lambda metric: metric.combined_score)
    return best.n_clusters, metrics


def fit_clusters(embedding, n_clusters: int, deps, seed: int):
    return deps.KMeans(
        n_clusters=n_clusters, random_state=seed, n_init=10, max_iter=300
    ).fit_predict(embedding)

