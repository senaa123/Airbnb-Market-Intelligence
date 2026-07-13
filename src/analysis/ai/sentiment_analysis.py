"""
sentiment_analysis.py
Section 7.1: Multilingual sentiment analysis on guest reviews, using a
transformer model instead of a lexicon-based tool (VADER), since Bangkok's
international guest base includes substantial non-English review text that
lexicon-based tools cannot score correctly (verified during development —
see decision log).
Usage: python src/analysis/ai/sentiment_analysis.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))

import pandas as pd
import numpy as np
import duckdb
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import matplotlib.pyplot as plt
from scipy import stats
from src.utils.config import load_config

MODEL_NAME = "cardiffnlp/twitter-xlm-roberta-base-sentiment"  # multilingual: covers ~100 languages
LABELS = ["Negative", "Neutral", "Positive"]


def load_model():
    print(f"Loading multilingual sentiment model ({MODEL_NAME})... this downloads once, then caches.")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()
    return tokenizer, model


def score_batch(texts, tokenizer, model, batch_size=32):
    """Scores a list of texts, returns compound-style scores in [-1, 1]
    (negative_prob * -1 + positive_prob * 1, same interpretable scale as before)."""
    scores = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        inputs = tokenizer(batch, return_tensors="pt", truncation=True, padding=True, max_length=256)
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=1).numpy()
        # probs columns are [negative, neutral, positive] per this model's label order
        compound = probs[:, 2] - probs[:, 0]  # positive_prob - negative_prob, range [-1, 1]
        scores.extend(compound.tolist())
        if (i // batch_size) % 20 == 0:
            print(f"  Scored {i + len(batch)}/{len(texts)} reviews...")
    return scores


def main():
    config = load_config()
    city = config["city"]["name"]
    raw_dir = Path(config["paths"]["raw_dir"]) / city
    processed_dir = Path(config["paths"]["processed_dir"])
    out_dir = Path("report/findings/section7_ai")
    fig_dir = Path("report/figures")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Loading reviews...")
    reviews = pd.read_csv(raw_dir / "reviews.csv.gz", compression="gzip", low_memory=False)
    reviews = reviews.dropna(subset=["comments"])
    print(f"Loaded {len(reviews)} reviews with text")

    # Sample for runtime — transformer inference is slower per-review than a lexicon
    # tool, so the sample is smaller than the earlier VADER attempt, but still large
    # enough for reliable pattern detection.
    sample_size = min(5000, len(reviews))
    reviews_sample = reviews.sample(n=sample_size, random_state=42).copy()
    print(f"Scoring sentiment on a random sample of {sample_size} reviews using a multilingual "
          f"transformer model (smaller sample than a lexicon-tool approach would use, since "
          f"transformer inference is slower — traded runtime for correctness on multilingual text)")

    tokenizer, model = load_model()

    texts = reviews_sample["comments"].astype(str).str[:500].tolist()  # truncate very long reviews
    print("Scoring sentiment (this will take a few minutes on CPU)...")
    reviews_sample["sentiment_score"] = score_batch(texts, tokenizer, model)

    print(f"\nSentiment score distribution:\n{reviews_sample['sentiment_score'].describe()}")

    reviews_sample["sentiment_category"] = pd.cut(
        reviews_sample["sentiment_score"],
        bins=[-1, -0.05, 0.05, 1],
        labels=["Negative", "Neutral", "Positive"]
    )
    print(f"\nSentiment categories:\n{reviews_sample['sentiment_category'].value_counts()}")

    reviews_sample[["listing_id", "date", "comments", "sentiment_score", "sentiment_category"]].to_csv(
        out_dir / "review_sentiment_scores.csv", index=False
    )

    # ---- Join to listing-level review scores ----
    db_path = processed_dir / f"{city}_warehouse.duckdb"
    con = duckdb.connect(str(db_path), read_only=True)
    listing_ratings = con.execute("""
        SELECT listing_id, review_scores_rating FROM fact_listings
        WHERE review_scores_rating IS NOT NULL
    """).df()
    con.close()

    listing_sentiment = reviews_sample.groupby("listing_id")["sentiment_score"].mean().reset_index()
    listing_sentiment.columns = ["listing_id", "avg_sentiment_score"]

    merged = listing_sentiment.merge(listing_ratings, on="listing_id", how="inner")
    print(f"\nListings with both sentiment and star rating: {len(merged)}")

    corr, p_value = stats.pearsonr(merged["avg_sentiment_score"], merged["review_scores_rating"])
    print(f"Correlation between avg sentiment and star rating: {corr:.3f} (p={p_value:.6f})")

    merged.to_csv(out_dir / "sentiment_vs_rating.csv", index=False)

    merged["rating_normalized"] = (merged["review_scores_rating"] - 1) / 4 * 2 - 1
    merged["divergence"] = merged["avg_sentiment_score"] - merged["rating_normalized"]

    print("\n=== Top 5: sentiment much MORE positive than star rating suggests ===")
    print(merged.nlargest(5, "divergence")[["listing_id", "avg_sentiment_score", "review_scores_rating", "divergence"]])

    print("\n=== Top 5: sentiment much MORE negative than star rating suggests ===")
    print(merged.nsmallest(5, "divergence")[["listing_id", "avg_sentiment_score", "review_scores_rating", "divergence"]])

    merged.to_csv(out_dir / "sentiment_rating_divergence.csv", index=False)

    # ---- Spot-check the most extreme divergence cases against actual text ----
    # (same verification discipline used for the price artifact investigation)
    check_ids = pd.concat([
        merged.nsmallest(3, "divergence")["listing_id"],
        merged.nlargest(3, "divergence")["listing_id"]
    ]).tolist()
    sample_check = reviews_sample[reviews_sample["listing_id"].isin(check_ids)][
        ["listing_id", "comments", "sentiment_score"]
    ]
    print("\n=== Verification: sample text for most extreme divergence cases ===")
    for _, row in sample_check.iterrows():
        print(f"\nListing {row['listing_id']} (sentiment={row['sentiment_score']:.3f}):")
        print(f"  {row['comments'][:300]}")

    # ---- Visualize ----
    plt.figure(figsize=(8, 6))
    plt.scatter(merged["review_scores_rating"], merged["avg_sentiment_score"], alpha=0.3, s=10)
    plt.xlabel("Star Rating (review_scores_rating)")
    plt.ylabel("Average Review Sentiment Score (multilingual model, -1 to 1)")
    plt.title(f"Figure 12: Sentiment vs. Star Rating (r={corr:.3f})")
    plt.tight_layout()
    plt.savefig(fig_dir / "fig12_sentiment_vs_rating.png")
    plt.close()
    print("\nSaved fig12_sentiment_vs_rating.png")

    print("\nSection 7.1 (Sentiment Analysis) complete.")


if __name__ == "__main__":
    main()