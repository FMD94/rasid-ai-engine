import csv
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report

from src.rasid.pipeline_ar_text_transformer import analyze_ar_text_transformer
from src.rasid.pipeline_en_text_transformer import analyze_en_text_transformer

y_true = []
y_pred = []

with open("data/eval/eval_dataset.csv", "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.reader(f)
    next(reader, None)

    for row in reader:
        if len(row) >= 4:
            text = row[1]
            true_label = row[2].lower().strip()
            lang = row[3].lower().strip()

            if lang == "ar":
                result = analyze_ar_text_transformer(text)
            else:
                result = analyze_en_text_transformer(text)

            y_true.append(true_label)
            y_pred.append(result["decision"].lower().strip())

labels = ["approved", "flagged", "blocked"]

cm = confusion_matrix(y_true, y_pred, labels=labels)
acc = accuracy_score(y_true, y_pred)

precision, recall, f1, _ = precision_recall_fscore_support(
    y_true, y_pred, labels=labels, average="macro", zero_division=0
)

print("\n=== RAW TRANSFORMER MODEL EVALUATION ===")
print("Samples used:", len(y_true))
print("Labels order:", labels)

print("\nConfusion Matrix:")
print(cm)

print("\nAccuracy:", round(acc * 100, 2), "%")
print("Precision:", round(precision, 4))
print("Recall:", round(recall, 4))
print("F1-Score:", round(f1, 4))

print("\nClassification Report:")
print(classification_report(
    y_true, y_pred,
    labels=labels,
    target_names=["Safe", "Manipulative", "Fraud"],
    zero_division=0
))