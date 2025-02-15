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
    locations = db.locations.distinct("location")
    return jsonify({"locations": locations})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        features = data.get('features', {})
        
        all_locations = db.locations.distinct("location")
        location_encoded = [1 if loc == features['location'] else 0 for loc in all_locations[1:]]
        
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
