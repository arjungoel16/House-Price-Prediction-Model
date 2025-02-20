from flask import Flask, request, jsonify
import pickle
import numpy as np
from pymongo import MongoClient
from flask_cors import CORS
from sklearn.preprocessing import StandardScaler
import threading
import os

# Initialize the Flask application
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Connect to MongoDB database
client = MongoClient("mongodb://localhost:27017/?directConnection=true&serverSelectionTimeoutMS=2000")
db = client.house_price_db

# Load pre-trained model from file
model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found: {model_path}")

with open(model_path, "rb") as f:
    model = pickle.load(f)

# Function to retrain the model asynchronously
def retrain_model():
    os.system("python train_model.py")

# API endpoint to retrieve available locations from the database
@app.route('/locations', methods=['GET'])
def get_locations():
    try:
        # Retrieve location names from the database
        locations_cursor = db.locations.find({}, {"_id": 0, "location": 1})
        locations = [loc["location"] for loc in locations_cursor if "location" in loc]

        if not locations:
            print("No locations found in the database.")  # Debugging log
            return jsonify({"locations": []}), 404

        return jsonify({"locations": locations})
    except Exception as e:
        print(f"Error fetching locations: {str(e)}")  # Debugging log
        return jsonify({"error": str(e)}), 500

# Load pre-trained model and scaler
scaler_path = os.path.join(os.path.dirname(__file__), "scaler.pkl")

if not os.path.exists(scaler_path):
    raise FileNotFoundError(f"Scaler file not found: {scaler_path}")

with open(scaler_path, "rb") as f:
    scaler = pickle.load(f)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        features = data.get('features', {})

        # Retrieve all locations
        existing_locations = db.locations.distinct("location")
        
        # If location is new, add it to the database
        if features['location'] not in existing_locations:
            db.locations.insert_one({"location": features['location']})
            existing_locations.append(features['location'])

        # Encode location as a one-hot vector
        location_encoded = [1 if loc == features['location'] else 0 for loc in existing_locations]

        # Convert input features into a NumPy array
        feature_array = np.array([
            float(features['size']),
            int(features['bedrooms']),
            int(features['bathrooms']),
            *location_encoded
        ]).reshape(1, -1)

        # Normalize input features using pre-trained scaler
        feature_array_scaled = scaler.transform(feature_array)

        # Predict house price using the pre-trained model
        prediction = model.predict(feature_array_scaled)[0]

        # Store prediction result in the database
        db.predictions.insert_one({"features": features, "predicted_price": prediction})

        return jsonify({"predicted_price": float(prediction)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API endpoint to retrain the model asynchronously
@app.route('/retrain', methods=['POST'])
def retrain():
    threading.Thread(target=retrain_model).start()
    return jsonify({"message": "Model retraining started."})

# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
