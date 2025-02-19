from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client.house_price_db

sample_data = [
    {"size": 1500, "bedrooms": 3, "bathrooms": 2, "location": "New York", "price": 500000},
    {"size": 1800, "bedrooms": 4, "bathrooms": 3, "location": "Los Angeles", "price": 700000},
    {"size": 1200, "bedrooms": 2, "bathrooms": 1, "location": "Chicago", "price": 350000},
    {"size": 1400, "bedrooms": 3, "bathrooms": 2, "location": "Houston", "price": 450000},
    {"size": 1600, "bedrooms": 4, "bathrooms": 3, "location": "Miami", "price": 550000},
    {"size": 1700, "bedrooms": 3, "bathrooms": 2, "location": "San Francisco", "price": 800000},
]

db.house_data.insert_many(sample_data)
print("Sample house data inserted.")
# adding sample data to the database. This script inserts sample house data into the MongoDB database.
# this is for training the model and testing the prediction functionality of the application.