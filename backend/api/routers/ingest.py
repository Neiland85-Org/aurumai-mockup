from fastapi import APIRouter, HTTPException
from models import RawMeasurement, FeatureVector
from infrastructure.db.database import get_connection

router = APIRouter()


@router.post("/raw")
async def ingest_raw(meas: RawMeasurement):
    """
    Ingest raw telemetry data from IoT devices/Edge nodes
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Verify machine exists
        cur.execute("SELECT machine_id FROM machines WHERE machine_id = ?", (meas.machine_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail=f"Machine {meas.machine_id} not found")

        # Insert all metrics
        for key, value in meas.metrics.items():
            cur.execute("""
                INSERT INTO raw_measurements (machine_id, timestamp, metric_key, metric_value)
                VALUES (?, ?, ?, ?)
            """, (meas.machine_id, meas.timestamp.isoformat(), key, value))

        conn.commit()
        conn.close()

        return {
            "status": "ok",
            "message": "raw data ingested",
            "machine_id": meas.machine_id,
            "metrics_count": len(meas.metrics)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/features")
async def ingest_features(vec: FeatureVector):
    """
    Ingest feature-engineered data from Edge nodes
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Verify machine exists
        cur.execute("SELECT machine_id FROM machines WHERE machine_id = ?", (vec.machine_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail=f"Machine {vec.machine_id} not found")

        # Insert all features
        for key, value in vec.features.items():
            cur.execute("""
                INSERT INTO features (machine_id, timestamp, feature_key, feature_value)
                VALUES (?, ?, ?, ?)
            """, (vec.machine_id, vec.timestamp.isoformat(), key, value))

        conn.commit()
        conn.close()

        return {
            "status": "ok",
            "message": "features ingested",
            "machine_id": vec.machine_id,
            "features_count": len(vec.features)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
