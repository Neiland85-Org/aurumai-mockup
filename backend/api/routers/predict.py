from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from models import PredictionRequest, PredictionResponse
from services.ml_engine import run_prediction
from infrastructure.db.database import get_connection

router = APIRouter()


@router.post("/", response_model=PredictionResponse)
async def predict(machine_id: str = Query(..., description="Machine ID to predict")):
    """
    Run predictive maintenance model for a specific machine
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Verify machine exists
        cur.execute("SELECT machine_id, machine_type FROM machines WHERE machine_id = ?", (machine_id,))
        machine = cur.fetchone()
        if not machine:
            raise HTTPException(status_code=404, detail=f"Machine {machine_id} not found")

        # Get latest features for prediction
        cur.execute("""
            SELECT feature_key, feature_value
            FROM features
            WHERE machine_id = ?
            ORDER BY timestamp DESC
            LIMIT 20
        """, (machine_id,))

        features_rows = cur.fetchall()
        if not features_rows:
            # If no features, use raw measurements
            cur.execute("""
                SELECT metric_key, metric_value
                FROM raw_measurements
                WHERE machine_id = ?
                ORDER BY timestamp DESC
                LIMIT 10
            """, (machine_id,))
            features_rows = cur.fetchall()

        features = {row["feature_key" if "feature_key" in dict(row) else "metric_key"]: row["feature_value" if "feature_value" in dict(row) else "metric_value"] for row in features_rows}

        # Run ML prediction
        prediction_result = run_prediction(machine_id, machine["machine_type"], features)

        timestamp = datetime.utcnow()

        # Store prediction
        cur.execute("""
            INSERT INTO predictions (
                machine_id, timestamp, risk_score, failure_probability,
                confidence, next_maintenance_hours
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            machine_id,
            timestamp.isoformat(),
            prediction_result["risk_score"],
            prediction_result["failure_probability"],
            prediction_result["confidence"],
            prediction_result["next_maintenance_hours"]
        ))

        conn.commit()
        conn.close()

        return PredictionResponse(
            machine_id=machine_id,
            timestamp=timestamp,
            risk_score=prediction_result["risk_score"],
            failure_probability=prediction_result["failure_probability"],
            confidence=prediction_result["confidence"],
            next_maintenance_hours=prediction_result["next_maintenance_hours"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{machine_id}")
async def get_prediction_history(machine_id: str, limit: int = Query(default=50, le=200)):
    """
    Get prediction history for a machine
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT machine_id, timestamp, risk_score, failure_probability,
                   confidence, next_maintenance_hours
            FROM predictions
            WHERE machine_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (machine_id, limit))

        rows = cur.fetchall()
        conn.close()

        return {
            "machine_id": machine_id,
            "predictions": [dict(row) for row in rows]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
