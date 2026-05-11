import pandas as pd
from collections import Counter
from src.rasid.pipeline_text_auto import analyze_text_auto

df = pd.read_csv(
    "data/eval/eval_dataset.csv",
    quotechar='"',
    escapechar="\\",
    on_bad_lines="skip"
)

df = df[["text", "label", "language"]].dropna()

correct = 0
total = len(df)

lang_total = Counter()
lang_correct = Counter()

label_total = Counter()
label_correct = Counter()

wrong_predictions = []

print("\n--- EVALUATION START ---\n")

for _, row in df.iterrows():
    text = row["text"]
    true_label = row["label"]
    lang = row["language"]

    result = analyze_text_auto(text)

    if result is None:
        result = {
            "decision": "error",
            "reasons": ["analyze_text_auto returned None"]
        }

    pred = result.get("decision")
    is_correct = pred == true_label

    lang_total[lang] += 1
    label_total[true_label] += 1

    if is_correct:
        correct += 1
        lang_correct[lang] += 1
        label_correct[true_label] += 1
    else:
        wrong_predictions.append({
            "text": text,
            "lang": lang,
            "true": true_label,
            "pred": pred,
            "reasons": result.get("reasons", [])
        })

    print(f"TEXT: {text}")
    print(f"LANG: {lang} | TRUE: {true_label} | PRED: {pred} | {'✔' if is_correct else '❌'}")
    print("-" * 60)

accuracy = correct / total

print("\n--- RESULTS ---")
print(f"Overall Accuracy: {accuracy:.2f} ({correct}/{total})")

print("\nBy Language:")
for lang in sorted(lang_total.keys()):
    acc = lang_correct[lang] / lang_total[lang]
    print(f"{lang}: {acc:.2f} ({lang_correct[lang]}/{lang_total[lang]})")

print("\nBy Label:")
for label in ["approved", "flagged", "blocked"]:
    if label_total[label] > 0:
        acc = label_correct[label] / label_total[label]
        print(f"{label}: {acc:.2f} ({label_correct[label]}/{label_total[label]})")

print("\n--- WRONG PREDICTIONS ONLY ---\n")

for item in wrong_predictions:
    print(f"TEXT: {item['text']}")
    print(f"LANG: {item['lang']}")
    print(f"TRUE: {item['true']} | PRED: {item['pred']}")
    print(f"REASONS: {item['reasons']}")
    print("-" * 60)