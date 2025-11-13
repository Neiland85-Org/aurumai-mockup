from fastapi import APIRouter, HTTPException
from typing import List
from models import MachineInfo, MachineMetrics
from infrastructure.db.database import get_connection
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=List[MachineInfo])
async def list_machines():
    """
    List all available machines
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT machine_id, machine_type, site, status, commissioned_date
            FROM machines
            ORDER BY machine_id
        """)

        machines = []
        for row in cur.fetchall():
            machines.append(MachineInfo(
                machine_id=row["machine_id"],
                machine_type=row["machine_type"],
                site=row["site"],
                status=row["status"],
                commissioned_date=datetime.fromisoformat(row["commissioned_date"]) if row["commissioned_date"] else None
            ))

        conn.close()
        return machines

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{machine_id}/metrics", response_model=MachineMetrics)
async def get_machine_metrics(machine_id: str):
    """
    Get current metrics and status for a specific machine
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Get machine info
        cur.execute("""
            SELECT machine_id, machine_type, site, status
            FROM machines
            WHERE machine_id = ?
        """, (machine_id,))

        machine_row = cur.fetchone()
        if not machine_row:
            raise HTTPException(status_code=404, detail=f"Machine {machine_id} not found")

        # Get latest measurements
        cur.execute("""
            SELECT metric_key, metric_value, timestamp
            FROM raw_measurements
            WHERE machine_id = ?
            ORDER BY timestamp DESC
            LIMIT 20
        """, (machine_id,))

        latest_metrics = {}
        last_timestamp = None
        for row in cur.fetchall():
            if row["metric_key"] not in latest_metrics:
                latest_metrics[row["metric_key"]] = row["metric_value"]
            if not last_timestamp:
                last_timestamp = datetime.fromisoformat(row["timestamp"])

        # Get latest prediction
        cur.execute("""
            SELECT risk_score, failure_probability, confidence, next_maintenance_hours, timestamp
            FROM predictions
            WHERE machine_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (machine_id,))

        prediction_row = cur.fetchone()
        prediction = None
        if prediction_row:
            from models import PredictionResponse
            prediction = PredictionResponse(
                machine_id=machine_id,
                timestamp=datetime.fromisoformat(prediction_row["timestamp"]),
                risk_score=prediction_row["risk_score"],
                failure_probability=prediction_row["failure_probability"],
                confidence=prediction_row["confidence"],
                next_maintenance_hours=prediction_row["next_maintenance_hours"]
            )

        # Count active alerts (for now just based on risk score)
        alerts_count = 0
        if prediction and prediction.risk_score > 0.6:
            alerts_count = 1
        elif prediction and prediction.risk_score > 0.4:
            alerts_count = 1

        conn.close()

        return MachineMetrics(
            machine_id=machine_id,
            current_status=machine_row["status"],
            last_measurement=last_timestamp,
            metrics=latest_metrics,
            alerts_count=alerts_count,
            predictions=prediction
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
