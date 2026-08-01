import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load dataset
df = pd.read_csv("dataset/cancer/Cancer.csv")

# Remove unnecessary columns
df = df.drop(columns=["id", "Unnamed: 32"])

# Convert diagnosis to numbers
# M = 1 (Malignant)
# B = 0 (Benign)
df["diagnosis"] = df["diagnosis"].map({"M": 1, "B": 0})

# Features and Target
X = df.drop("diagnosis", axis=1)
y = df["diagnosis"]

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Train Model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# Accuracy
pred = model.predict(X_test)
accuracy = accuracy_score(y_test, pred)

print(f"Accuracy: {accuracy * 100:.2f}%")

# Save Model
joblib.dump(model, "models/cancer.pkl")

print("Model saved successfully!")
# Print feature names
print("\nFeatures used by the model:")
print(X.columns.tolist())