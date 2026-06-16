from __future__ import annotations


def save_metric_plot(metrics, selected: int, output_dir, deps):
    if not metrics:
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    x = [metric.n_clusters for metric in metrics]
    fig, axes = deps.plt.subplots(3, 1, figsize=(8, 10), sharex=True)
    series = [
        [metric.silhouette for metric in metrics],
        [metric.davies_bouldin for metric in metrics],
        [metric.calinski_harabasz for metric in metrics],
    ]
    titles = [
        "Silhouette Score",
        "Davies-Bouldin Index",
        "Calinski-Harabasz Index",
    ]

    for ax, y, title in zip(axes, series, titles):
        ax.plot(x, y, marker="o")
        ax.axvline(selected, color="red", linestyle="--", linewidth=1)
        ax.set_ylabel(title)
        ax.grid(True, alpha=0.3)

    axes[-1].set_xlabel("Number of clusters")
    fig.tight_layout()
    fig.savefig(output_dir / "cluster_evaluation_metrics.png", dpi=300, bbox_inches="tight")
    deps.plt.close(fig)


def save_embedding_plots(embedding, labels, ids, cfg, deps):
    marked = set(str(x) for x in cfg.ids_to_mark)

    if embedding.shape[1] < 2:
        return

    fig, ax = deps.plt.subplots(figsize=(6, 6))
    ax.scatter(embedding[:, 0], embedding[:, 1], c=labels, cmap="tab20", s=50, alpha=0.72)
    for idx, mol_id in enumerate(ids):
        if str(mol_id) in marked:
            ax.scatter(
                embedding[idx, 0],
                embedding[idx, 1],
                s=160,
                color="black",
                marker="x",
                linewidths=2,
                zorder=10,
            )
    ax.set_title(f"{cfg.feature_type} features + UMAP + KMeans")
    ax.set_xlabel("UMAP 1")
    ax.set_ylabel("UMAP 2")
    fig.tight_layout()
    fig.savefig(cfg.output_dir / f"umap_{cfg.feature_type}_clusters.png", dpi=300, bbox_inches="tight")
    deps.plt.close(fig)

    if embedding.shape[1] <= 2:
        return

    plot_dir = cfg.output_dir / "umap_dimension_plots"
    plot_dir.mkdir(parents=True, exist_ok=True)

    for dim in range(embedding.shape[1]):
        fig, ax = deps.plt.subplots(figsize=(6, 6))
        ax.hist(embedding[:, dim], bins=30)
        ax.set_title(f"UMAP {dim + 1} Distribution")
        ax.set_xlabel(f"UMAP {dim + 1}")
        ax.set_ylabel("Frequency")
        fig.tight_layout()
        fig.savefig(plot_dir / f"umap{dim + 1}_histogram.png", dpi=300, bbox_inches="tight")
        deps.plt.close(fig)

    for x_dim in range(embedding.shape[1]):
        for y_dim in range(x_dim + 1, embedding.shape[1]):
            fig, ax = deps.plt.subplots(figsize=(6, 6))
            ax.scatter(
                embedding[:, x_dim],
                embedding[:, y_dim],
                c=labels,
                cmap="tab20",
                s=50,
                alpha=0.72,
            )
            for idx, mol_id in enumerate(ids):
                if str(mol_id) in marked:
                    ax.scatter(
                        embedding[idx, x_dim],
                        embedding[idx, y_dim],
                        s=160,
                        color="black",
                        marker="x",
                        linewidths=2,
                        zorder=10,
                    )
            ax.set_title(f"UMAP {x_dim + 1} vs UMAP {y_dim + 1}")
            ax.set_xlabel(f"UMAP {x_dim + 1}")
            ax.set_ylabel(f"UMAP {y_dim + 1}")
            fig.tight_layout()
            fig.savefig(
                plot_dir / f"umap{x_dim + 1}_vs_umap{y_dim + 1}.png",
                dpi=300,
                bbox_inches="tight",
            )
            deps.plt.close(fig)

