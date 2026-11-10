
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
FINANCIAL_FILE = Path("data/processed/financial_exceptions.csv")


def evaluate_fraud_detection(results, truth):
    print("\n========== FRAUD DETECTION EVALUATION ==========")

    evaluation = results.merge(
        truth[["claim_id", "is_fraud"]],
        on="claim_id",
        how="inner",
        validate="one_to_one"
    )

    if evaluation.empty:
        print("No labelled claims available for evaluation.")
        return

    y_true = evaluation["is_fraud"].astype(int)
    y_pred = (evaluation["risk_score"] >= 30).astype(int)

    print("Total claims:", len(results))
    print("Labelled claims:", len(evaluation))
    print("Known fraud cases:", int(y_true.sum()))
    print("Known genuine cases:", int((y_true == 0).sum()))

    # Calculate full classification metrics only when both classes exist
    if y_true.nunique() == 2:
        print(f"Precision: {precision_score(y_true, y_pred):.2f}")
        print(f"Recall: {recall_score(y_true, y_pred):.2f}")
        print(f"F1-score: {f1_score(y_true, y_pred):.2f}")

        print("\nConfusion matrix:")
        print(confusion_matrix(y_true, y_pred, labels=[0, 1]))
    else:
        print(
            "\nFull precision, recall and F1 evaluation is not "
            "reliable because the labelled data contains only "
            "one class."
        )

        positive_cases = int(y_true.sum())

        if positive_cases > 0:
            detected = int(
                ((y_true == 1) & (y_pred == 1)).sum()
            )

            print(
                f"Known fraud detection coverage: "
                f"{detected}/{positive_cases}"
            )

    print("\nKnown labelled case results:")

    print(
        evaluation[
            ["claim_id", "is_fraud", "risk_score", "risk_reasons"]
        ].to_string(index=False)
    )

    print(
        "\nNote: Unlabelled claims are not assumed to be genuine."
    )


def evaluate_financial_detection(truth):
    print("\n========== FINANCIAL ANOMALY EVALUATION ==========")

    if not FINANCIAL_FILE.exists():
        print("Financial exceptions file not found.")
        return

    if "fraud_pattern" not in truth.columns:
        print("Ground truth has no fraud_pattern column.")
        return

    exceptions = pd.read_csv(FINANCIAL_FILE)

    if exceptions.empty:
        print("No financial exceptions detected.")
        return

    exceptions["search_text"] = (
        exceptions["exception_type"].fillna("").astype(str)
        + " "
        + exceptions["description"].fillna("").astype(str)
    ).str.lower()

    truth["fraud_pattern"] = (
        truth["fraud_pattern"].fillna("").astype(str).str.lower()
    )

    checks = [
        (
            "Duplicate invoice",
            "duplicate invoice",
            ["duplicate", "invoice"]
        ),
        (
            "Payment exceeds approved amount",
            "payment exceeds approved amount",
            ["payment", "exceed"]
        )
    ]

    for title, expected_text, keywords in checks:
        expected_ids = set(
            truth.loc[
                truth["fraud_pattern"].str.contains(
                    expected_text, regex=False
                ),
                "claim_id"
            ]
        )

        detected_ids = set(
            exceptions.loc[
                exceptions["search_text"].apply(
                    lambda value: all(
                        keyword in value for keyword in keywords
                    )
                ),
                "claim_id"
            ].dropna()
        )

        matched = expected_ids.intersection(detected_ids)

        print(f"\n{title}:")
        print("Expected labelled claims:", len(expected_ids))
        print("Detected labelled claims:", len(matched))

        if expected_ids:
            print(
                "Detection coverage:",
                f"{len(matched) / len(expected_ids):.2f}"
            )
        else:
            print("No corresponding ground-truth cases found.")

    print(
        "\nNote: Detection coverage is not precision. "
        "Unlabelled financial records cannot be assumed genuine."
    )


def evaluate_model():
    print("Evaluating insurance fraud detection system...\n")

    if not RESULTS_FILE.exists() or not TRUTH_FILE.exists():
        raise FileNotFoundError(
            "Required evaluation files are missing. "
            "Run the data generation and detection pipeline first."
        )

    results = pd.read_csv(RESULTS_FILE)
    truth = pd.read_csv(TRUTH_FILE)

    required_results = {"claim_id", "risk_score", "risk_reasons"}
    required_truth = {"claim_id", "is_fraud", "fraud_pattern"}

    if not required_results.issubset(results.columns):
        raise ValueError("Fraud results are missing required columns.")

    if not required_truth.issubset(truth.columns):
        raise ValueError("Ground truth is missing required columns.")

    if results["claim_id"].duplicated().any():
        raise ValueError("Duplicate claim IDs in fraud results.")

    if truth["claim_id"].duplicated().any():
        raise ValueError("Duplicate claim IDs in ground truth.")

    truth["is_fraud"] = pd.to_numeric(
        truth["is_fraud"], errors="raise"
    )

    if not truth["is_fraud"].isin([0, 1]).all():
        raise ValueError("Ground-truth labels must be 0 or 1.")

    results["risk_score"] = pd.to_numeric(
        results["risk_score"], errors="raise"
    )

    missing = set(truth["claim_id"]) - set(results["claim_id"])

    if missing:
        raise ValueError(
            f"Unknown claim IDs in ground truth: {missing}"
        )

    evaluate_fraud_detection(results, truth)
    evaluate_financial_detection(truth)

    print("\nEvaluation completed.")


if __name__ == "__main__":
    evaluate_model()
