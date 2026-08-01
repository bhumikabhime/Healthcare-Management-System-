import os
import tensorflow as tf
from keras.src.legacy.preprocessing.image import ImageDataGenerator

# ==============================
# Dataset Path
# ==============================

DATASET_PATH = "dataset/chest_xray"

TRAIN_DIR = os.path.join(DATASET_PATH, "train")
VAL_DIR = os.path.join(DATASET_PATH, "val")
TEST_DIR = os.path.join(DATASET_PATH, "test")

# ==============================
# Image Settings
# ==============================

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32

# ==============================
# Data Generators
# ==============================

train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=15,
    zoom_range=0.2,
    horizontal_flip=True,
    validation_split=0.20
)

# ==============================
# Load Dataset
# ==============================

train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",
    subset="training",
    shuffle=True
)

val_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",
    subset="validation",
    shuffle=False
)

test_datagen = ImageDataGenerator(
    rescale=1./255
)

test_generator = test_datagen.flow_from_directory(
    TEST_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",
    shuffle=False
)

# ==============================
# Information
# ==============================

print("\n==============================")
print("Dataset Loaded Successfully")
print("==============================")

print("\nClass Mapping:")
print(train_generator.class_indices)

print("\nTraining Images :", train_generator.samples)
print("Validation Images:", val_generator.samples)
print("Testing Images :", test_generator.samples)

print("\nImage Size :", IMAGE_SIZE)
print("Batch Size :", BATCH_SIZE)