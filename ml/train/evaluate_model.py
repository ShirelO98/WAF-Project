import os
import pandas as pd
import joblib
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

def main():
    # Define paths
    base_dir   = os.path.abspath(os.path.dirname(__file__))
    test_path  = os.path.join(base_dir, '..', 'data', 'test_data.csv')
    model_path = os.path.join(base_dir, '..', 'model', 'isolation_forest.pkl')

    # Load test data
    df = pd.read_csv(test_path)
    
    # Use the exact same features as in train_model.py
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
    y_true = df['label']

    # Load trained model
    model = joblib.load(model_path)

    # Compute anomaly scores and raw predictions (-1 = anomaly)
    anomaly_scores = model.decision_function(X)
    raw_preds      = model.predict(X)

    # Map to binary labels: 1 = attack, 0 = normal
    y_pred = (raw_preds == -1).astype(int)

    # Print metrics
    print("=== Classification Report ===")
    print(classification_report(y_true, y_pred))
    print("=== Confusion Matrix ===")
    print(confusion_matrix(y_true, y_pred))

    # Compute ROC AUC if possible
    try:
        auc = roc_auc_score(y_true, -anomaly_scores)
        print(f"ROC AUC: {auc:.3f}")
    except Exception as e:
        print(f"Could not compute ROC AUC: {e}")

if __name__ == '__main__':
    main()
