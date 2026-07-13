"""
segmentation.py
Section 6.3: K-Means clustering to segment hosts/listings by behavior.
Usage: python src/analysis/datascience/segmentation.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
from src.utils.config import load_config


def main():
    config = load_config()
    city = config["city"]["name"]
    processed_dir = Path(config["paths"]["processed_dir"])
    out_dir = Path("report/findings/section6_datascience")
    fig_dir = Path("report/figures")
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(processed_dir / f"ml_features_{city}.parquet")

    # Feature set for clustering, as planned: host portfolio size + listing performance metrics
    cluster_features = [
        "calculated_host_listings_count", "price", "occupancy_rate_pct",
        "review_scores_rating", "number_of_reviews", "availability_365"
    ]
    X = df[cluster_features].copy()
    print(f"Clustering on {len(X)} listings, features: {cluster_features}")

    # Standardize — K-Means is distance-based, and these features are on very
    # different scales (price in thousands, ratings 0-5, listings count 1-100+)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ---- Try k=3 to 6, pick best by silhouette score ----
    print("\n=== Silhouette scores by k ===")
    silhouette_scores = {}
    for k in range(3, 7):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, labels)
        silhouette_scores[k] = score
        print(f"k={k}: silhouette score = {score:.4f}")

    best_k = max(silhouette_scores, key=silhouette_scores.get)
    print(f"\nBest k by silhouette score: {best_k}")

    # ---- Fit final model with best k ----
    kmeans_final = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    df["cluster"] = kmeans_final.fit_predict(X_scaled)

    # ---- Profile each cluster ----
    print(f"\n=== Cluster Profiles (k={best_k}) ===")
    profile = df.groupby("cluster")[cluster_features].mean().round(2)
    profile["n_listings"] = df.groupby("cluster").size()
    print(profile)
    profile.to_csv(out_dir / "cluster_profiles.csv")

    # Sanity check: is Cluster 5's low rating a genuine quality signal, or an
    # artifact of the median-imputation applied to unreviewed listings during
    # feature engineering? Confirms whether has_reviews skews toward False.
    print("\n=== Cluster 5 has_reviews check (verifying low rating is genuine) ===")
    print(df[df["cluster"] == 5]["has_reviews"].value_counts())

    # ---- Visualize: silhouette score by k ----
    plt.figure(figsize=(7, 5))
    plt.plot(list(silhouette_scores.keys()), list(silhouette_scores.values()), marker="o")
    plt.axvline(best_k, color="red", linestyle="--", alpha=0.5, label=f"Best k={best_k}")
    plt.xlabel("Number of Clusters (k)")
    plt.ylabel("Silhouette Score")
    plt.title("Figure 10: Silhouette Score by Number of Clusters")
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_dir / "fig10_silhouette_scores.png")
    plt.close()
    print("Saved fig10_silhouette_scores.png")

    # ---- Visualize: cluster profiles as a heatmap-style bar comparison ----
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for ax, feature in zip(axes.flatten(), cluster_features):
        profile[feature].plot(kind="bar", ax=ax, color="steelblue")
        ax.set_title(feature)
        ax.set_xlabel("Cluster")
    plt.suptitle(f"Figure 11: Cluster Profiles (k={best_k})")
    plt.tight_layout()
    plt.savefig(fig_dir / "fig11_cluster_profiles.png")
    plt.close()
    print("Saved fig11_cluster_profiles.png")

    df[["listing_id", "cluster"] + cluster_features].to_csv(out_dir / "listing_clusters.csv", index=False)
    print(f"\nSaved full cluster assignments to listing_clusters.csv")
    print("\nSection 6.3 (Segmentation) complete.")


if __name__ == "__main__":
    main()