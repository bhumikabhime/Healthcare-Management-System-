import os
import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    roc_curve,
    auc
)

from tensorflow.keras.models import load_model

from data_loader import test_generator

# ==============================
# Load Model
# ==============================

model = load_model("models/pneumonia_model.keras")

# ==============================
# Predict
# ==============================

test_generator.reset()

predictions = model.predict(test_generator)

y_prob = predictions.ravel()
y_pred = (y_prob > 0.5).astype(int)

y_true = test_generator.classes

# ==============================
# Accuracy
# ==============================

accuracy = np.mean(y_pred == y_true)

print("\n==============================")
print("Test Accuracy")
print("==============================")
print(f"{accuracy*100:.2f}%")

# ==============================
# Classification Report
# ==============================

print("\n==============================")
print("Classification Report")
print("==============================")

print(
    classification_report(
        y_true,
        y_pred,
        target_names=["NORMAL", "PNEUMONIA"]
    )
)

# ==============================
# Create Results Folder
# ==============================

os.makedirs("results", exist_ok=True)

# ==============================
# Confusion Matrix
# ==============================

cm = confusion_matrix(y_true, y_pred)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["NORMAL", "PNEUMONIA"]
)

disp.plot(cmap="Blues")

plt.title("Confusion Matrix")

plt.savefig("results/confusion_matrix.png")

plt.show()

# ==============================
# ROC Curve
# ==============================

fpr, tpr, _ = roc_curve(y_true, y_prob)

roc_auc = auc(fpr, tpr)

plt.figure(figsize=(6,6))

plt.plot(fpr, tpr, label=f"AUC = {roc_auc:.3f}")

plt.plot([0,1],[0,1],'k--')

plt.xlabel("False Positive Rate")

plt.ylabel("True Positive Rate")

plt.title("ROC Curve")

plt.legend()

plt.savefig("results/roc_curve.png")

plt.show()

print(f"\nAUC Score : {roc_auc:.4f}")

print("\nGraphs saved in results/")