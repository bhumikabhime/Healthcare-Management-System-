from data_loader import train_generator, val_generator
from model import build_model
import os
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# Build Model
model = build_model()

# Show Model Summary
model.summary()

# Create models folder if it doesn't exist
os.makedirs("models", exist_ok=True)

# Callbacks
checkpoint = ModelCheckpoint(
    "models/pneumonia_model.keras",
    monitor="val_accuracy",
    save_best_only=True
)

early_stop = EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True
)

# Train Model
history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=10,
    callbacks=[checkpoint, early_stop]
)

# Save History
import pickle

with open("models/history.pkl", "wb") as f:
    pickle.dump(history.history, f)

print("\nTraining History Saved!")