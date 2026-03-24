from sklearn.ensemble import IsolationForest
import numpy as np


class AnomalyDetector:

    def __init__(self, logger):
        self.logger = logger
        self.model = IsolationForest(contamination=0.1)

    def detect(self, metrics_history):

        try:

            data = np.array(metrics_history)

            if len(data) < 10:
                return {"anomaly": False}

            self.model.fit(data)

            prediction = self.model.predict(data[-1].reshape(1, -1))

            return {
                "anomaly": prediction[0] == -1
            }

        except Exception as e:
            self.logger.error(f"ML anomaly detection failed: {e}")
            return {"anomaly": False}