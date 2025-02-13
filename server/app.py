from flask import Flask, request, jsonify
import pickle
import numpy as np
from pymongo import MongoClient
from flask_cors import CORS

CORS(app)


app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.house_price_db

# Load the trained model (you need to train and save it beforehand)
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

@app.route('/locations', methods=['GET'])
def get_locations():
    # Get distinct locations from MongoDB
    locations = db.locations.distinct("location")
    return jsonify({"locations": locations})

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    features = data['features']

    # Preprocess the location (convert to an ID or use the location directly)
    location = features['location']

    # Retrieve the location_id from MongoDB (or map directly if necessary)
    location_data = db.locations.find_one({"location": location})
    location_id = location_data['_id'] if location_data else None

    if not location_id:
        return jsonify({"error": "Invalid location"}), 400

    # Prepare the feature array (example for size, bedrooms, bathrooms, and location_id)
    feature_array = np.array([features['size'], features['bedrooms'], features['bathrooms'], location_id]).reshape(1, -1)

    # Predict the house price using the model
    prediction = model.predict(feature_array)

    return jsonify({"predicted_price": prediction[0]})

if __name__ == "__main__":
    app.run(debug=True)
