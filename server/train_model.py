import pandas as pd
import pickle
from pymongo import MongoClient
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import os

def connect_db():
    """Connects to MongoDB and returns the database object."""
    return MongoClient("mongodb://localhost:27017/?directConnection=true&serverSelectionTimeoutMS=2000").house_price_db

def fetch_data(db):
    """Fetches house data from the database and prepares it for training."""
    house_data = list(db.house_data.find({}, {"_id": 0, "size": 1, "bedrooms": 1, "bathrooms": 1, "location": 1, "price": 1}))

    if not house_data:
        print("No house data found.")
        return None

    df = pd.DataFrame(house_data)
    df = pd.get_dummies(df, columns=["location"], drop_first=True)

    return df.dropna()

def train_and_save_model(df):
    """Trains a RandomForest and XGBoost model, selects the best, and saves it along with the scaler."""
    X, y = df.drop(columns=['price']), df['price']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    # Train Random Forest
    param_grid = {'n_estimators': [100, 200], 'max_depth': [None, 10]}
    rf = RandomForestRegressor()
    grid_search = GridSearchCV(rf, param_grid, cv=min(2, len(X_train)), scoring='r2')
    grid_search.fit(X_train, y_train)
    best_rf_model = grid_search.best_estimator_
    best_rf_model.fit(X_train, y_train)

    # Train XGBoost
    xgb_model = XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=5)
    xgb_model.fit(X_train, y_train)

    # Predict on test data
    y_pred_rf = best_rf_model.predict(X_test)
    y_pred_xgb = xgb_model.predict(X_test)

    # Save the best model based on R2 score
    metrics = {
        "RandomForest": {
            "MAE": mean_absolute_error(y_test, y_pred_rf),
            "MSE": mean_squared_error(y_test, y_pred_rf),
            "R2": r2_score(y_test, y_pred_rf),
        },
        "XGBoost": {
            "MAE": mean_absolute_error(y_test, y_pred_xgb),
            "MSE": mean_squared_error(y_test, y_pred_xgb),
            "R2": r2_score(y_test, y_pred_xgb),
        },
    }

    best_model = best_rf_model if metrics["RandomForest"]["R2"] > metrics["XGBoost"]["R2"] else xgb_model

    # Save the best model
    with open("model.pkl", "wb") as f:
        pickle.dump(best_model, f)

    # Save the scaler
    with open("scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    print("Model and scaler saved successfully.")
    print("Performance Metrics:", metrics)

    # Save metrics in the database
    db = connect_db()
    db.model_metrics.insert_one(metrics)

def retrain_model():
    """Triggers model retraining."""
    os.system("python train_model.py")

def main():
    """Main function to fetch data and train the model if data exists."""
    db = connect_db()
    df = fetch_data(db)

    if df is not None and not df.empty:
        train_and_save_model(df)
    else:
        print("Skipping model training due to insufficient data.")

if __name__ == "__main__":
    main()
