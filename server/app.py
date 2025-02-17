from flask import Flask, request, jsonify
import pickle
import numpy as np
from pymongo import MongoClient
from flask_cors import CORS
from sklearn.preprocessing import StandardScaler
import threading
import os

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://localhost:27017/")
db = client.house_price_db

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

def retrain_model():
    os.system("python train_model.py")

@app.route('/locations', methods=['GET'])
def get_locations():
    try:
        # Fetch all unique locations from MongoDB
        locations_cursor = db.locations.find({}, {"_id": 0, "location": 1})
        locations = [loc["location"] for loc in locations_cursor if "location" in loc]

        if not locations:
            return jsonify({"locations": []}), 404  # Return empty if no locations found

        return jsonify({"locations": locations})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        features = data.get('features', {})

        # Check if the location is new and add it to the database
        existing_locations = db.locations.distinct("location")
        if features['location'] not in existing_locations:
            db.locations.insert_one({"location": features['location']})

        # Encode location as a one-hot vector
        location_encoded = [1 if loc == features['location'] else 0 for loc in existing_locations]

        feature_array = np.array([
            float(features['size']),
            int(features['bedrooms']),
            int(features['bathrooms']),
            *location_encoded
        ]).reshape(1, -1)

        scaler = StandardScaler()
        feature_array_scaled = scaler.fit_transform(feature_array)

        prediction = model.predict(feature_array_scaled)[0]

        db.predictions.insert_one({"features": features, "predicted_price": prediction})

        return jsonify({"predicted_price": float(prediction)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/retrain', methods=['POST'])
def retrain():
    threading.Thread(target=retrain_model).start()
    return jsonify({"message": "Model retraining started."})

if __name__ == "__main__":
    app.run(debug=True)
