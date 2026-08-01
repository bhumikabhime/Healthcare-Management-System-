import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ===============================
# Load Dataset
# ===============================

df = pd.read_csv("dataset/diabetes/diabetes.csv")

print(df.head())

# ===============================
# Features and Target
# ===============================

X = df.drop("Outcome", axis=1)
y = df["Outcome"]

# ===============================
# Train Test Split
# ===============================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# ===============================
# Train Model
# ===============================

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

# ===============================
# Prediction
# ===============================

y_pred = model.predict(X_test)

# ===============================
# Accuracy
# ===============================

accuracy = accuracy_score(y_test, y_pred)

print("\nAccuracy:", accuracy)

print("\nClassification Report\n")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix\n")
print(confusion_matrix(y_test, y_pred))

# ===============================
# Save Model
# ===============================

joblib.dump(model, "models/diabetes.pkl")

print("\nModel saved successfully!")