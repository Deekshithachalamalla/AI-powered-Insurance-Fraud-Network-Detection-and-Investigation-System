
import pandas as pd
from pathlib import Path
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

RESULTS_FILE = Path("data/processed/fraud_results.csv")
TRUTH_FILE = Path("data/ground_truth/ground_truth.csv")


def evaluate_model():
    print("Evaluating fraud detection system...\n")

    results = pd.read_csv(RESULTS_FILE)
    truth = pd.read_csv(TRUTH_FILE)

    # Check that claim IDs are unique
    if results["claim_id"].duplicated().any():
        raise ValueError("Duplicate claim IDs in fraud results")

    if truth["claim_id"].duplicated().any():
        raise ValueError("Duplicate claim IDs in ground truth")

    # Check that all labelled claims exist in the results
    missing = set(truth["claim_id"]) - set(results["claim_id"])
    if missing:
        raise ValueError(f"Unknown claim IDs in ground truth: {missing}")

    # Only evaluate claims with known labels
    evaluation = results.merge(
        truth[["claim_id", "is_fraud"]],
        on="claim_id",
        how="inner",
        validate="one_to_one"
    )

    # Predicted suspicious if risk score >= 30
    y_true = evaluation["is_fraud"].astype(int)
    y_pred = (evaluation["risk_score"] >= 30).astype(int)

    precision = precision_score(
        y_true, y_pred, zero_division=0
    )
    recall = recall_score(
        y_true, y_pred, zero_division=0
    )
    f1 = f1_score(
        y_true, y_pred, zero_division=0
    )

    print("EVALUATION RESULTS")
    print("--------------------------")
    print("Total claims:", len(results))
    print("Labelled test claims:", len(evaluation))
    print("Planted positive cases:", int(y_true.sum()))
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1-score: {f1:.2f}")

    print("\nConfusion matrix:")
    print(confusion_matrix(y_true, y_pred, labels=[0, 1]))

    print("\nIndividual planted case results:")
    print(
        evaluation[
            ["claim_id", "is_fraud", "risk_score", "risk_reasons"]
        ].to_string(index=False)
    )

    if len(evaluation) < len(results):
        print(
            "\nIMPORTANT: These metrics cover labelled cases only."
        )
        print(
            "Unlabelled claims cannot be assumed to be genuine."
        )


if __name__ == "__main__":
    evaluate_model()
