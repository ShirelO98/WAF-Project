import os
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

def main():
    # Define paths
    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_path = os.path.join(base_dir, '..', 'data', 'traffic_log.csv')
    model_dir = os.path.join(base_dir, '..', 'model')
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'isolation_forest.pkl')

    # Load CSV data
    df = pd.read_csv(data_path, parse_dates=['timestamp'])

    # Select numeric features for training
    feature_cols = [
        'packet_size',
        'inter_arrival_time',
        'header_size',
        'num_headers',
        'connection_duration',
        'packets_per_connection',
        'avg_payload_per_request',
        'bytes_sent',
        'bytes_received'
    ]
    X = df[feature_cols]

    # Initialize and train Isolation Forest
    model = IsolationForest(
        n_estimators=100,
        contamination=0.1,
        random_state=42
    )
    model.fit(X)

    # Save the trained model
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == '__main__':
    main()
