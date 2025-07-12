import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime

class SlowlorisDetector:
    """
    Maintains per-connection stats and uses a trained IsolationForest
    to flag Slowloris-like behavior.
    """

    def __init__(self, model_path):
        # Load the pre-trained IsolationForest model
        self.model = joblib.load(model_path)

        # Feature names must match the order used during model training
        self.feature_names = [
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

        # In-memory state for each client connection
        # keyed by (client_ip, client_port)
        self.state = {}

    def record_request(self, conn_key, header_bytes, payload_bytes):
        """
        Update per-connection statistics each time a new request arrives.
        conn_key: tuple (client_ip, client_port)
        header_bytes: int, size of all HTTP headers in bytes
        payload_bytes: int, size of the request body in bytes
        """
        now_ts = datetime.utcnow().timestamp()
        st = self.state.get(conn_key)

        if st is None:
            # First request on this connection
            st = {
                'first_ts': now_ts,
                'last_ts': now_ts,
                'packets': 1,
                'header_bytes': header_bytes,
                'payload_bytes': payload_bytes,
                'header_count': 1
            }
        else:
            # Update running totals
            st['packets']       += 1
            st['header_bytes']  += header_bytes
            st['payload_bytes'] += payload_bytes
            st['header_count']  += 1
            st['last_ts']       = now_ts

        self.state[conn_key] = st

    def extract_features(self, conn_key):
        """
        Build a one-row DataFrame of features for the given connection.
        Returns None if the connection is unknown.
        """
        st = self.state.get(conn_key)
        if st is None:
            return None

        # Compute time-based features
        duration      = st['last_ts'] - st['first_ts']
        inter_arrival = duration / max(st['packets'], 1)
        avg_payload   = st['payload_bytes'] / max(st['packets'], 1)

        # Construct a single-row dict
        row = {
            'packet_size':             st['header_bytes'] + st['payload_bytes'],
            'inter_arrival_time':      inter_arrival,
            'header_size':             st['header_bytes'],
            'num_headers':             st['header_count'],
            'connection_duration':     duration,
            'packets_per_connection':  st['packets'],
            'avg_payload_per_request': avg_payload,
            'bytes_sent':              st['payload_bytes'],
            'bytes_received':          0  # unknown in this context
        }

        # Return a DataFrame with correct column order
        return pd.DataFrame([row], columns=self.feature_names)

    def is_slowloris(self, conn_key, min_requests=5):
        """
        Return True if the connection is flagged as Slowloris.
        Only start classifying after at least `min_requests` have arrived.
        """
        st = self.state.get(conn_key)
        if st is None or st['packets'] < min_requests:
            # Not enough data to decide yet
            return False

        X = self.extract_features(conn_key)
        if X is None:
            return False

        # Predict: -1 = anomaly (potential Slowloris), 1 = normal
        pred = self.model.predict(X)[0]
        return pred == -1