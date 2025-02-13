from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.house_price_db

# Sample locations to insert into the `locations` collection
locations = ["New York", "Los Angeles", "Chicago", "San Francisco", "Austin"]

# Insert locations into the `locations` collection
for location in locations:
    if db.locations.count_documents({"location": location}) == 0:  # Check if the location already exists
        db.locations.insert_one({"location": location})
        print(f"Inserted location: {location}")

# Sample house data to insert into the `house_data` collection
house_data = [
    {"size": 1200, "bedrooms": 3, "bathrooms": 2, "location": "New York", "price": 500000},
    {"size": 800, "bedrooms": 2, "bathrooms": 1, "location": "Los Angeles", "price": 350000},
    {"size": 1500, "bedrooms": 4, "bathrooms": 3, "location": "Chicago", "price": 750000},
    {"size": 2000, "bedrooms": 4, "bathrooms": 3, "location": "San Francisco", "price": 1200000},
    {"size": 1100, "bedrooms": 3, "bathrooms": 2, "location": "Austin", "price": 450000}
]

# Insert house data into the `house_data` collection
for house in house_data:
    if db.house_data.count_documents({"size": house["size"], "location": house["location"]}) == 0:  # Check if the house data already exists
        db.house_data.insert_one(house)
        print(f"Inserted house data: {house}")

print("Data insertion complete!")
