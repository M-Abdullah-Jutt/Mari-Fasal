from fastapi import FastAPI, File, UploadFile
import uvicorn
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf
import torch
import cv2
import sys
import os
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.append(PROJECT_ROOT)

from Models.Plant_Segmentation.infer_severity_local import load_model, estimate_severity

SEVERITY_MODEL_PATH = os.path.join(PROJECT_ROOT, "Models", "Plant_Segmentation", "v1", "plantseg_unet_disease.pth")
DISEASE_MODEL_PATH = os.path.join(PROJECT_ROOT, "Models", "Plant_Disease_Prediction", "v1", "tf_lite_diseases_detection_model.tflite")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
severity_model = load_model(SEVERITY_MODEL_PATH, device)

interpreter = tf.lite.Interpreter(model_path=DISEASE_MODEL_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

TARGET_SIZE = (128, 128)

CLASS_NAMES = ['Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy', 'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy', 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_', 'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy', 'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy', 'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy', 'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy', 'Raspberry___healthy', 'Soybean___healthy', 'Squash___Powdery_mildew', 'Strawberry___Leaf_scorch', 'Strawberry___healthy', 'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus', 'Tomato___healthy']

app = FastAPI()

def read_file_as_image(data) -> np.ndarray:
    
    img = Image.open(BytesIO(data)).convert("RGB")
    
    img = img.resize(TARGET_SIZE)
    
    img_array = np.array(img, dtype=np.float32) 
    
    return img_array

@app.post("/predict-disease")
async def predict(file: UploadFile = File(...)):
    # Read and process data
    image = read_file_as_image(await file.read())

    # Adds the batch dimension -> transforms (128, 128, 3) into (1, 128, 128, 3)
    img_batch = np.expand_dims(image, axis=0)

    # Invoke TFLite model safely using index keys
    interpreter.set_tensor(input_details[0]['index'], img_batch)
    interpreter.invoke()

    raw_predictions = interpreter.get_tensor(output_details[0]['index'])

    predictions = raw_predictions[0]


    predicted_class_idx = np.argmax(predictions)

    predicted_class = CLASS_NAMES[predicted_class_idx]

    raw_confidence = float(predictions[predicted_class_idx])


    return {
        "class": predicted_class,
        "confidence_raw": round(raw_confidence, 4),             
        "confidence_percentage": f"{round(raw_confidence * 100, 2)}%"
    }


# Disease Severity Program

def read_file_as_cv2_image(data) -> np.ndarray:
    img = Image.open(BytesIO(data)).convert("RGB")
    img_array = np.array(img)
    return cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)


import tempfile #because the severity model needs file path so we are using tempfile

@app.post("/predict-severity")
async def predict_severity(file: UploadFile = File(...)):
    raw_bytes = await file.read()
    image = read_file_as_cv2_image(raw_bytes)
    result = estimate_severity(image, severity_model, device)
    return {
        "severity_percentage": result["severity_pct"],
        "plant_pixels": result["plant_pixels"],
        "disease_pixels": result["disease_pixels"],
    }


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
