from __future__ import annotations


def preprocess_for_umap(features, cfg, deps):
    n_samples, n_features = features.shape
    if n_samples < 2 or n_features < 2:
        return features, {"pca_components": float(n_features), "pca_explained_variance": 1.0}

    max_components = max(1, min(cfg.pca_components, n_samples - 1, n_features))
    if max_components < 2:
        return features, {"pca_components": float(n_features), "pca_explained_variance": 1.0}

    pca = deps.PCA(n_components=max_components, random_state=cfg.random_state)
    reduced = pca.fit_transform(features)
    return reduced, {
        "pca_components": float(max_components),
        "pca_explained_variance": float(deps.np.sum(pca.explained_variance_ratio_)),
    }


def run_umap(features, cfg, deps):
    reducer = deps.umap.UMAP(
        n_components=cfg.umap_components,
        random_state=cfg.random_state,
        n_neighbors=min(cfg.umap_neighbors, max(2, len(features) - 1)),
        min_dist=cfg.umap_min_dist,
        metric=cfg.umap_metric,
        spread=1.0,
    )
    return reducer.fit_transform(features)

