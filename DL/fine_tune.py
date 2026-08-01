import os
import pickle
import tensorflow as tf

from tensorflow.keras.models import load_model
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

from data_loader import train_generator, val_generator

# ===========================
# Load Existing Model
# ===========================

model = load_model("models/pneumonia_model.keras")

# ===========================
# Unfreeze MobileNetV2 Layers
# ===========================

print("\nModel Layers:\n")

for i, layer in enumerate(model.layers):
    print(i, layer.name, type(layer))
    
# ===========================
# Compile Again
# ===========================

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

# ===========================
# Callbacks
# ===========================

checkpoint = ModelCheckpoint(
    "models/pneumonia_model_finetuned.keras",
    monitor="val_accuracy",
    save_best_only=True
)

early_stop = EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True
)

# ===========================
# Train
# ===========================

history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=10,
    callbacks=[checkpoint, early_stop]
)

# ===========================
# Save History
# ===========================

with open("models/history_finetune.pkl", "wb") as f:
    pickle.dump(history.history, f)

print("\nFine-Tuning Completed Successfully!")