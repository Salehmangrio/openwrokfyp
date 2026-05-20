from __future__ import annotations

import numpy as np
from fastapi import APIRouter
from sklearn.ensemble import IsolationForest

from app.schemas import FraudDetectRequest

router = APIRouter(tags=["fraud"])


@router.post("/ai/fraud-detect")
async def fraud(payload: FraudDetectRequest):
    # Align all three series to the same length (truncate to min length) and
    # require at least a couple of samples for IsolationForest to be useful.
    series = [payload.loginPatterns, payload.bidAmounts, payload.responseTimes]
    if any(len(s) == 0 for s in series):
        return {"fraudProbability": 0.0, "flags": [], "anomalies": []}

    min_len = min(len(s) for s in series)
    if min_len < 2:
        return {"fraudProbability": 0.0, "flags": [], "anomalies": []}

    X = np.array(
        [
            payload.loginPatterns[:min_len],
            payload.bidAmounts[:min_len],
            payload.responseTimes[:min_len],
        ],
        dtype=float,
    ).T

    model = IsolationForest(contamination="auto", random_state=42, n_estimators=100)
    model.fit(X)
    preds = model.predict(X)  # 1 = normal, -1 = anomaly

    anomaly_indices = [int(i) for i, p in enumerate(preds) if p == -1]
    risk = float(len(anomaly_indices)) / float(len(preds))

    flags = []
    if risk >= 0.6:
        flags.append("high_risk")
    elif risk >= 0.3:
        flags.append("moderate_risk")

    return {
        "fraudProbability": round(risk, 3),
        "flags": flags,
        "anomalies": anomaly_indices,
    }
