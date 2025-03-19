import os
import json
import pandas as pd
import numpy as np
import tensorflow as tf
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
from tensorflow.keras.preprocessing import image
from PIL import Image

# Load trained model
MODEL_PATH = os.path.join(settings.BASE_DIR, "plant_disease_model.h5")
model = tf.keras.models.load_model(MODEL_PATH)

# Load CSV files
DISEASE_INFO_PATH = os.path.join(settings.BASE_DIR, "disease_info.csv")
SUPPLEMENT_INFO_PATH = os.path.join(settings.BASE_DIR, "supplement_info.csv")
CLASS_NAMES_PATH = os.path.join(settings.BASE_DIR, "class_names.json")

disease_df = pd.read_csv(DISEASE_INFO_PATH)
supplement_df = pd.read_csv(SUPPLEMENT_INFO_PATH)

# Load class names as a list
with open(CLASS_NAMES_PATH, "r") as f:
    class_names = json.load(f)


def preprocess_image(image_obj):
    """Preprocess image for model prediction."""
    img = image_obj.convert("RGB")  # ✅ Convert RGBA to RGB if needed
    img = img.resize((224, 224))  # Resize
    img = np.array(img) / 255.0  # Normalize pixel values
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    return img


def predict_image(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("image")

        if uploaded_file:
            # ✅ Process uploaded image
            file_path = default_storage.save(uploaded_file.name, uploaded_file)
            img_url = settings.MEDIA_URL + file_path
            img = Image.open(os.path.join(settings.MEDIA_ROOT, file_path))

            # ✅ Preprocess and predict
            img = preprocess_image(img)
            prediction = model.predict(img)
            predicted_class_index = np.argmax(prediction, axis=1)[0]
            
            # ✅ Fetch the predicted disease name correctly
            result = class_names[predicted_class_index]  # ✅ Corrected!

            # ✅ Case-insensitive match for disease details
            matching_rows = disease_df[disease_df["disease_name"].str.lower() == result.lower()]

            if not matching_rows.empty:
                disease_details = matching_rows.iloc[0].to_dict()
                disease_info = {
                    "description": disease_details.get("description", "No description available"),
                    "steps": disease_details.get("Possible Steps", "No steps available"),
                    "image_url": disease_details.get("image_url", ""),
                }
            else:
                disease_info = {
                    "description": "No description available.",
                    "steps": "No steps available.",
                    "image_url": "",
                }

            # ✅ Case-insensitive match for supplement details
            supplement_details = supplement_df[supplement_df["disease_name"].str.lower() == result.lower()].to_dict(orient="records")
            supplements = [
                {
                    "supplement_name": supp.get("supplement_name", "No supplement"),
                    "supplement_image": supp.get("supplement_image", ""),
                    "supplement_url": supp.get("buy_link", "#"),
                }
                for supp in supplement_details
            ]

            # ✅ Pass details to result.html
            return render(request, "result.html", {
                "uploaded_image": img_url,
                "result": result,
                "disease_details": disease_info,
                "supplement_details": supplements,
            })

    # Show upload page if not POST request
    return render(request, "upload.html")


def home(request):
    return render(request, "home.html")
