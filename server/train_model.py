import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pickle
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.house_price_db


# Fetch data from MongoDB
house_data = db.house_data.find()

# Convert the data to a DataFrame
df = pd.DataFrame(list(house_data))

# Preprocess the data (convert categorical location to numerical)
df['location'] = df['location'].apply(lambda x: db.locations.find_one({"location": x})['_id'])

X = df[['size', 'bedrooms', 'bathrooms', 'location']]
y = df['price']

# Train the model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)

# Save the trained model
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)
