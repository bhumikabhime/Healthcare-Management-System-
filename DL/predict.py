import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# ==============================
# Load Model (only once)
# ==============================

model = load_model("models/pneumonia_model.keras")

IMAGE_SIZE = (224, 224)

# ==============================
# Prediction Function
# ==============================

def predict_xray(image_path):
    """
    Predict whether the chest X-ray is NORMAL or PNEUMONIA.
    Returns:
        prediction (str)
        confidence (float)
    """

    # Load image
    img = image.load_img(image_path, target_size=IMAGE_SIZE)

    # Convert to array
    img_array = image.img_to_array(img)

    # Normalize
    img_array = img_array / 255.0

    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)

    # Predict
    probability = model.predict(img_array, verbose=0)[0][0]

    if probability >= 0.5:
        prediction = "PNEUMONIA"
        confidence = probability * 100
    else:
        prediction = "NORMAL"
        confidence = (1 - probability) * 100

    return prediction, round(float(confidence), 2)


# ==============================
# Test
# ==============================

if __name__ == "__main__":

    img_path = "Test.jpeg"     # Replace with your own image

    result, confidence = predict_xray(img_path)

    print("Prediction :", result)
    print("Confidence :", confidence, "%")