from pymongo import MongoClient

def connect_db():
    return MongoClient("mongodb://localhost:27017/").house_price_db

def insert_locations(db):
    locations = ["New York", "Los Angeles", "Chicago", "San Francisco", "Austin"]
    existing_locations = set(db.locations.distinct("location"))

    new_entries = [{"location": loc} for loc in locations if loc not in existing_locations]
    if new_entries:
        db.locations.insert_many(new_entries)
        print(f"Inserted {len(new_entries)} new locations.")

def insert_house_data(db):
    house_data = [
        {"size": 1200, "bedrooms": 3, "bathrooms": 2, "location": "New York", "price": 500000},
        {"size": 800, "bedrooms": 2, "bathrooms": 1, "location": "Los Angeles", "price": 350000},
    ]

    for house in house_data:
        if not db.house_data.find_one({"size": house["size"], "location": house["location"]}):
            db.house_data.insert_one(house)

def main():
    db = connect_db()
    insert_locations(db)
    insert_house_data(db)
    print("Data insertion complete!")

if __name__ == "__main__":
    main()
