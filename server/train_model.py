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
    return MongoClient("mongodb://localhost:27017/").house_price_db

def fetch_data(db):
    house_data = list(db.house_data.find({}, {"_id": 0, "size": 1, "bedrooms": 1, "bathrooms": 1, "location": 1, "price": 1}))
    
    if not house_data:
        print("No house data found.")
        return None
    
    df = pd.DataFrame(house_data)
    df = pd.get_dummies(df, columns=["location"], drop_first=True)
    
    return df.dropna()

def train_and_save_model(df):
    X, y = df.drop(columns=['price']), df['price']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    
    param_grid = {'n_estimators': [100, 200], 'max_depth': [None, 10]}
    rf = RandomForestRegressor()
    # ensuring cv never exceeds the number of samples in the training set
    grid_search = GridSearchCV(rf, param_grid, cv=min(2, len(X_train)), scoring='r2')
    grid_search.fit(X_train, y_train)
    best_rf_model = grid_search.best_estimator_
    best_rf_model.fit(X_train, y_train)
    
    xgb_model = XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=5)
    xgb_model.fit(X_train, y_train)
    
    y_pred_rf = best_rf_model.predict(X_test)
    y_pred_xgb = xgb_model.predict(X_test)
    
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
    with open("model.pkl", "wb") as f:
        pickle.dump(best_model, f)
    
    print("Model training complete and saved as 'model.pkl'.")
    print("Performance Metrics:", metrics)
    
    db = connect_db()
    db.model_metrics.insert_one(metrics)

def retrain_model():
    os.system("python train_model.py")

def main():
    db = connect_db()
    df = fetch_data(db)
    
    if df is not None and not df.empty:
        train_and_save_model(df)
    else:
        print("Skipping model training due to insufficient data.")

if __name__ == "__main__":
    main()
