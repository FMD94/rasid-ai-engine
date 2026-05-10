from pathlib import Path
import pandas as pd
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

MODEL_NAME = "aubmindlab/bert-base-arabertv2"

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "ar" / "text_ads.csv"
OUT_DIR = ROOT / "models" / "ar_transformer"

label2id = {"approved": 0, "flagged": 1, "blocked": 2}
id2label = {0: "approved", 1: "flagged", 2: "blocked"}

df = pd.read_csv(DATA_PATH)

df = df[["text", "label"]].dropna()

df["text"] = df["text"].astype(str)

label2id = {"approved": 0, "flagged": 1, "blocked": 2}
df["label_id"] = df["label"].map(label2id)

train_df, test_df = train_test_split(
    df, test_size=0.2, random_state=42, stratify=df["label_id"]
)

train_ds = Dataset.from_pandas(
    train_df[["text", "label_id"]].rename(columns={"label_id": "labels"})
)
test_ds = Dataset.from_pandas(
    test_df[["text", "label_id"]].rename(columns={"label_id": "labels"})
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize(batch):
    return tokenizer(
        batch["text"],
        truncation=True,
        padding="max_length",
        max_length=128
    )

train_ds = train_ds.map(tokenize, batched=True)
test_ds = test_ds.map(tokenize, batched=True)

cols = ["input_ids", "attention_mask", "labels"]
train_ds.set_format(type="torch", columns=cols)
test_ds.set_format(type="torch", columns=cols)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=3,
    id2label=id2label,
    label2id=label2id
)
import torch
class_weights = torch.tensor([1.0, 2.0, 1.5]).to(model.device)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = logits.argmax(axis=-1)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average="macro"
    )
    acc = accuracy_score(labels, preds)
    return {
        "accuracy": acc,
        "macro_f1": f1,
        "macro_precision": precision,
        "macro_recall": recall,
    }

from transformers import Trainer
import torch.nn as nn

class WeightedTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.get("labels")

        outputs = model(**inputs)
        logits = outputs.get("logits")

        loss_fct = nn.CrossEntropyLoss(weight=class_weights)
        loss = loss_fct(logits, labels)

        return (loss, outputs) if return_outputs else loss

args = TrainingArguments(
    output_dir=str(OUT_DIR),
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=5,
    weight_decay=0.01,
    load_best_model_at_end=True,
    logging_dir=str(OUT_DIR / "logs"),
    report_to="none"
)

trainer = WeightedTrainer(
    model=model,
    args=args,
    train_dataset=train_ds,
    eval_dataset=test_ds,
    processing_class=tokenizer,
    compute_metrics=compute_metrics
)

trainer.train()
trainer.save_model(str(OUT_DIR))
tokenizer.save_pretrained(str(OUT_DIR))