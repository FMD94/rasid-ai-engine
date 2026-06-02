import csv
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)

from src.rasid.pipeline_text_auto import analyze_text_auto


rows = []

with open("data/eval/eval_dataset.csv", "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.reader(f)

    header = next(reader, None)

    for row in reader:
        if len(row) >= 4:
            rows.append({
                "id": row[0],
                "text": row[1],
                "label": row[2].lower().strip(),
                "language": row[3].lower().strip()
            })

df = pd.DataFrame(rows)

y_true = []
y_pred = []

for _, row in df.iterrows():
    result = analyze_text_auto(str(row["text"]))

    y_true.append(row["label"])
    y_pred.append(str(result.get("decision", "")).lower().strip())

labels = ["approved", "flagged", "blocked"]

cm = confusion_matrix(y_true, y_pred, labels=labels)
acc = accuracy_score(y_true, y_pred)

precision, recall, f1, _ = precision_recall_fscore_support(
    y_true,
    y_pred,
    labels=labels,
    average="macro",
    zero_division=0
)

print("\n=== CURRENT RASID EVALUATION ===")
print("Samples used:", len(y_true))

print("\nLabels order:")
print(labels)

print("\nConfusion Matrix:")
print(cm)

print("\nAccuracy:", round(acc * 100, 2), "%")
print("Precision:", round(precision, 4))
print("Recall:", round(recall, 4))
print("F1-Score:", round(f1, 4))

print("\nClassification Report:")
print(classification_report(
    y_true,
    y_pred,
    labels=labels,
    target_names=["Safe", "Manipulative", "Fraud"],
    zero_division=0
))