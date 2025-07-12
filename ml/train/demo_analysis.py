import os
import pandas as pd
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt

def main():
    # Define paths
    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_path = os.path.join(base_dir, '..', 'data', 'test_data.csv')

    # Load test data
    df = pd.read_csv(data_path, parse_dates=['timestamp'])
    feature_cols = [
        'inter_arrival_time',
        'connection_duration',
        'packet_size'
    ]
    X = df[feature_cols]

    # Train a fresh Isolation Forest on the test features (demo-only)
    model = IsolationForest(n_estimators=100, contamination=0.3, random_state=42)
    model.fit(X)

    # Compute anomaly scores and labels
    df['anomaly_score'] = model.decision_function(X)
    df['anomaly'] = model.predict(X)  # -1 = anomaly, 1 = normal

    # Separate normal vs suspected attacks
    normal = df[df['anomaly'] == 1]
    attacks = df[df['anomaly'] == -1]

    # 1) Anomaly Score Distribution
    plt.figure(figsize=(8, 5))
    plt.hist(normal['anomaly_score'], bins=50, alpha=0.7, label='Normal')
    plt.hist(attacks['anomaly_score'], bins=50, alpha=0.7, label='Detected as Slowloris')
    plt.title('Anomaly Score Distribution')
    plt.xlabel('Anomaly Score')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # 2) Inter-arrival Time Comparison
    plt.figure(figsize=(8, 5))
    plt.hist(normal['inter_arrival_time'], bins=50, alpha=0.7, label='Normal')
    plt.hist(attacks['inter_arrival_time'], bins=50, alpha=0.7, label='Detected as Slowloris')
    plt.title('Inter-arrival Time (s)')
    plt.xlabel('Inter-arrival Time')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # 3) Connection Duration Comparison
    plt.figure(figsize=(8, 5))
    plt.hist(normal['connection_duration'], bins=50, alpha=0.7, label='Normal')
    plt.hist(attacks['connection_duration'], bins=50, alpha=0.7, label='Detected as Slowloris')
    plt.title('Connection Duration (s)')
    plt.xlabel('Connection Duration')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
