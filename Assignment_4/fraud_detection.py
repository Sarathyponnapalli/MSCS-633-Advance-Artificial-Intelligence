"""
Unsupervised credit card fraud detection with a PyOD AutoEncoder.

Hands-On Assignment 4 - Advanced Artificial Intelligence (MSCS-633-M20)

An AutoEncoder learns to compress each transaction into a small code and
rebuild it. Trained on unlabeled data that is almost entirely legitimate, it
rebuilds ordinary transactions well and unusual ones badly, so the
reconstruction error works as a fraud score. The fraud labels in the dataset
are used only to evaluate the detector, never to train it.

Usage:
    python fraud_detection.py [--epochs 20] [--batch-size 256]
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
import urllib.request
from pathlib import Path
from typing import TextIO, cast

import matplotlib

matplotlib.use("Agg")  # render plots to files; no display inside Docker
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from matplotlib.ticker import MaxNLocator
from pyod.models.auto_encoder import AutoEncoder
from pyod.utils.utility import precision_n_scores
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split

# The Kaggle "Credit Card Fraud Detection" dataset (ULB, September 2013).
# Kaggle requires a login, so the identical file is fetched from the public
# TensorFlow mirror unless a copy already exists at --data.
DATA_URL = "https://storage.googleapis.com/download.tensorflow.org/data/creditcard.csv"
EXPECTED_ROWS = 284_807
LABEL = "Class"  # 1 = fraud, 0 = legitimate

# Colors from the dataviz reference palette: one fixed hue per class.
LEGIT_COLOR = "#2a78d6"   # blue
FRAUD_COLOR = "#eb6834"   # orange
INK = "#0b0b0b"           # primary text
MUTED_INK = "#52514e"     # secondary text, baselines
GRID = "#e4e3df"


class Tee:
    """Write console output to the terminal and keep a copy for results.txt."""

    def __init__(self, stream: TextIO):
        self.stream = stream
        self.lines: list[str] = []

    def __getattr__(self, name: str):
        # Anything else (isatty, encoding, fileno, ...) goes to the real stream.
        return getattr(self.stream, name)

    def write(self, text: str) -> int:
        self.lines.append(text)
        return self.stream.write(text)

    def flush(self) -> None:
        self.stream.flush()

    def getvalue(self) -> str:
        return "".join(self.lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=(__doc__ or "").strip().split("\n")[0])
    parser.add_argument("--data", type=Path, default=Path("data/creditcard.csv"),
                        help="path to creditcard.csv (downloaded if missing)")
    parser.add_argument("--output", type=Path, default=Path("output"),
                        help="folder for metrics, plots and the run log")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--test-size", type=float, default=0.3)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def set_seed(seed: int) -> None:
    """Make the split, weight initialization and batching reproducible."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def load_dataset(path: Path) -> pd.DataFrame:
    """Load the transactions, downloading them on first use."""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Downloading dataset to {path} ...")
        # Download to a temporary name so an interrupted run never leaves a
        # truncated CSV behind that later runs would trust.
        partial = path.with_suffix(".part")
        urllib.request.urlretrieve(DATA_URL, partial)  # nosec B310 - fixed https URL
        partial.replace(path)

    df = pd.read_csv(path)
    if len(df) != EXPECTED_ROWS or LABEL not in df.columns:
        raise ValueError(
            f"{path} does not look like the credit card fraud dataset "
            f"({len(df)} rows; expected {EXPECTED_ROWS} with a '{LABEL}' column)."
        )
    return df


def prepare_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Split the table into model inputs and the evaluation-only label.

    V1-V28 are already PCA components. Time (seconds since the first
    transaction) says nothing about the transaction itself, so it is dropped.
    Amount is heavily skewed, so log1p brings large purchases into the same
    range as the other features. PyOD then standardizes every column.
    """
    features = df.drop(columns=["Time", LABEL])
    features["Amount"] = np.log1p(features["Amount"])
    return features, df[LABEL]


def train_autoencoder(X_train: np.ndarray, contamination: float,
                      epochs: int, batch_size: int, seed: int) -> AutoEncoder:
    """
    Fit the AutoEncoder on unlabeled transactions.

    :param contamination: expected share of fraud. It only decides where the
        fraud/legit threshold sits on the score scale; training itself never
        sees a label.
    """
    model = AutoEncoder(
        # 29 inputs -> 64 -> 32 -> 16 (bottleneck) -> 32 -> 64 -> 29 outputs.
        # The narrow middle forces the network to learn the common patterns.
        hidden_neuron_list=[64, 32, 16],
        epoch_num=epochs,
        batch_size=batch_size,
        lr=1e-3,
        dropout_rate=0.1,
        batch_norm=True,
        contamination=contamination,
        preprocessing=True,  # standardize features inside PyOD
        random_state=seed,
        verbose=2,           # one line per epoch, parsed for the loss plot
    )
    model.fit(X_train)
    return model


def evaluate(y_true: np.ndarray, scores: np.ndarray, labels: np.ndarray) -> dict:
    """Score the detector against the held-out fraud labels."""
    tn, fp, fn, tp = confusion_matrix(y_true, labels).ravel()
    # output_dict=True returns a dict; the cast tells the type checker so.
    report = cast(dict, classification_report(
        y_true, labels, target_names=["legit", "fraud"], output_dict=True, zero_division=0
    ))
    return {
        # Ranking quality, independent of the threshold. Average precision
        # (area under the precision-recall curve) is the honest one here:
        # with 0.17% fraud, a random ranking scores about 0.0017.
        "roc_auc": roc_auc_score(y_true, scores),
        "average_precision": average_precision_score(y_true, scores),
        # Precision among the n highest scores, n = number of real frauds.
        "precision_at_n": precision_n_scores(y_true, scores),
        # Quality at the contamination threshold.
        "precision": report["fraud"]["precision"],
        "recall": report["fraud"]["recall"],
        "f1": report["fraud"]["f1-score"],
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "classification_report": report,
    }


def parse_epoch_losses(log: str) -> list[float]:
    """PyOD prints 'Epoch i/N, loss=x, ...' per epoch but doesn't store it."""
    return [float(x) for x in re.findall(r"Epoch \d+/\d+, loss=([0-9.]+)", log)]


def style_axes(ax: plt.Axes) -> None:
    """Thin, recessive axes so the data stands out."""
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED_INK)
    ax.tick_params(colors=MUTED_INK, labelcolor=INK)
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def plot_training_loss(losses: list[float], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    epochs = range(1, len(losses) + 1)
    ax.plot(epochs, losses, color=LEGIT_COLOR, linewidth=2, marker="o", markersize=4)
    ax.set_title("Training loss (mean squared reconstruction error)", color=INK, loc="left")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))  # whole epochs only
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    style_axes(ax)
    fig.tight_layout()
    fig.savefig(str(path), dpi=150)
    plt.close(fig)


def plot_reconstruction_error(scores: np.ndarray, y_true: np.ndarray,
                              threshold: float, path: Path) -> None:
    """Histogram of test-set scores per class, with the decision threshold."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    # Log-spaced bins because scores span several orders of magnitude.
    # The floor keeps log10 finite if a transaction is rebuilt perfectly.
    bins = np.logspace(np.log10(max(scores.min(), 1e-6)), np.log10(scores.max()), 60)
    # density=True so 148 frauds are visible next to 85,000 legit transactions.
    ax.hist(scores[y_true == 0], bins=bins, density=True, alpha=0.75,
            color=LEGIT_COLOR, label=f"Legitimate (n={int((y_true == 0).sum()):,})")
    ax.hist(scores[y_true == 1], bins=bins, density=True, alpha=0.75,
            color=FRAUD_COLOR, label=f"Fraud (n={int((y_true == 1).sum()):,})")
    ax.axvline(threshold, color=INK, linestyle="--", linewidth=1.5)
    ax.annotate(f"threshold = {threshold:.2f}", xy=(threshold, ax.get_ylim()[1] * 0.92),
                xytext=(6, 0), textcoords="offset points", color=INK, fontsize=9)
    ax.set_xscale("log")
    ax.set_title("Reconstruction error on the test set", color=INK, loc="left")
    ax.set_xlabel("Reconstruction error (anomaly score, log scale)")
    ax.set_ylabel("Density")
    ax.legend(frameon=False)
    style_axes(ax)
    fig.tight_layout()
    fig.savefig(str(path), dpi=150)
    plt.close(fig)


def plot_roc_pr(y_true: np.ndarray, scores: np.ndarray, metrics: dict, path: Path) -> None:
    """ROC and precision-recall curves side by side, each with its chance line."""
    fig, (roc_ax, pr_ax) = plt.subplots(1, 2, figsize=(11, 4.5))

    fpr, tpr, _ = roc_curve(y_true, scores)
    roc_ax.plot(fpr, tpr, color=LEGIT_COLOR, linewidth=2)
    roc_ax.plot([0, 1], [0, 1], color=MUTED_INK, linestyle=":", linewidth=1)
    roc_ax.text(0.55, 0.47, "random guess", color=MUTED_INK, fontsize=9, rotation=38)
    roc_ax.set_title(f"ROC curve (AUC = {metrics['roc_auc']:.3f})", color=INK, loc="left")
    roc_ax.set_xlabel("False positive rate")
    roc_ax.set_ylabel("True positive rate (recall)")

    precision, recall, _ = precision_recall_curve(y_true, scores)
    base_rate = y_true.mean()
    pr_ax.plot(recall, precision, color=LEGIT_COLOR, linewidth=2)
    pr_ax.axhline(base_rate, color=MUTED_INK, linestyle=":", linewidth=1)
    pr_ax.text(0.02, base_rate + 0.02, f"random guess ({base_rate:.2%})", color=MUTED_INK, fontsize=9)
    # Mark where the contamination threshold puts the detector.
    pr_ax.plot(metrics["recall"], metrics["precision"], "o", color=FRAUD_COLOR,
               markersize=8, markeredgecolor="white", markeredgewidth=2)
    pr_ax.annotate("chosen threshold", xy=(metrics["recall"], metrics["precision"]),
                   xytext=(8, 6), textcoords="offset points", color=INK, fontsize=9)
    pr_ax.set_title(f"Precision-recall (AP = {metrics['average_precision']:.3f})",
                    color=INK, loc="left")
    pr_ax.set_xlabel("Recall")
    pr_ax.set_ylabel("Precision")

    for ax in (roc_ax, pr_ax):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1.02)
        style_axes(ax)
    fig.tight_layout()
    fig.savefig(str(path), dpi=150)
    plt.close(fig)


def plot_confusion_matrix(cm: dict, path: Path) -> None:
    matrix = np.array([[cm["tn"], cm["fp"]], [cm["fn"], cm["tp"]]])
    fig, ax = plt.subplots(figsize=(5, 4.3))
    # Log color scale so the small fraud cells aren't all the same pale shade.
    ax.imshow(np.log10(matrix + 1), cmap="Blues")
    for (row, col), count in np.ndenumerate(matrix):
        dark_cell = np.log10(count + 1) > np.log10(matrix.max() + 1) * 0.6
        ax.text(col, row, f"{count:,}", ha="center", va="center", fontsize=13,
                color="white" if dark_cell else INK)
    ax.set_xticks([0, 1], labels=["Legit", "Fraud"])
    ax.set_yticks([0, 1], labels=["Legit", "Fraud"])
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion matrix (test set)", color=INK, loc="left")
    fig.tight_layout()
    fig.savefig(str(path), dpi=150)
    plt.close(fig)


def print_summary(metrics: dict, threshold: float) -> None:
    cm = metrics["confusion_matrix"]
    print("\n=== Results on the held-out test set ===")
    print(f"ROC-AUC                    {metrics['roc_auc']:.4f}")
    print(f"Average precision (PR-AUC) {metrics['average_precision']:.4f}")
    print(f"Precision @ n              {metrics['precision_at_n']:.4f}")
    print(f"Threshold                  {threshold:.4f}")
    print(f"Precision (fraud)          {metrics['precision']:.4f}")
    print(f"Recall (fraud)             {metrics['recall']:.4f}")
    print(f"F1 (fraud)                 {metrics['f1']:.4f}")
    print("\nConfusion matrix      predicted legit  predicted fraud")
    print(f"  actual legit        {cm['tn']:>15,}  {cm['fp']:>15,}")
    print(f"  actual fraud        {cm['fn']:>15,}  {cm['tp']:>15,}")


def main() -> None:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    tee = Tee(sys.stdout)
    sys.stdout = tee
    set_seed(args.seed)
    started = time.time()

    df = load_dataset(args.data)
    X, y = prepare_features(df)
    print(f"Loaded {len(df):,} transactions, {int(y.sum()):,} fraudulent "
          f"({y.mean():.3%}), {X.shape[1]} features.")

    # Stratify so the train and test sets keep the same tiny fraud share.
    X_train, X_test, y_train, y_test = train_test_split(
        X.to_numpy(), y.to_numpy(), test_size=args.test_size,
        stratify=y, random_state=args.seed,
    )
    print(f"Train: {len(X_train):,} rows | Test: {len(X_test):,} rows "
          f"({int(y_test.sum())} frauds held out for evaluation)")

    contamination = float(y_train.mean())  # the only label-derived input
    print(f"\nTraining AutoEncoder for {args.epochs} epochs "
          f"(contamination = {contamination:.5f}) ...")
    model = train_autoencoder(X_train, contamination, args.epochs, args.batch_size, args.seed)

    # Higher score = worse reconstruction = more likely fraud.
    scores = model.decision_function(X_test)
    labels = model.predict(X_test)
    metrics = evaluate(y_test, scores, labels)
    metrics.update({
        "threshold": float(model.threshold_),
        "contamination": contamination,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "test_frauds": int(y_test.sum()),
    })
    print_summary(metrics, model.threshold_)

    losses = parse_epoch_losses(tee.getvalue())
    metrics["epoch_losses"] = losses
    if losses:
        plot_training_loss(losses, args.output / "training_loss.png")
    plot_reconstruction_error(scores, y_test, model.threshold_, args.output / "reconstruction_error.png")
    plot_roc_pr(y_test, scores, metrics, args.output / "roc_pr_curves.png")
    plot_confusion_matrix(metrics["confusion_matrix"], args.output / "confusion_matrix.png")

    # .item() turns numpy scalars (e.g. sklearn's support counts) into JSON numbers.
    (args.output / "metrics.json").write_text(json.dumps(metrics, indent=2, default=lambda o: o.item()))
    print(f"\nSaved metrics and plots to {args.output}/ in {time.time() - started:.0f}s.")

    sys.stdout = tee.stream
    (args.output / "results.txt").write_text(tee.getvalue())


if __name__ == "__main__":
    main()
