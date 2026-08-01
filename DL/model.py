import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Model

IMAGE_SIZE = (224, 224, 3)

def build_model():

    # Load pretrained MobileNetV2 (without top classifier)
    base_model = MobileNetV2(
        weights="imagenet",
        include_top=False,
        input_shape=IMAGE_SIZE
    )

    # Freeze pretrained layers
    base_model.trainable = False

    x = base_model.output
    x = GlobalAveragePooling2D()(x)

    x = Dense(256, activation="relu")(x)
    x = Dropout(0.3)(x)

    output = Dense(1, activation="sigmoid")(x)

    model = Model(inputs=base_model.input, outputs=output)

    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )

    return model
if __name__ == "__main__":
    model = build_model()
    model.summary()