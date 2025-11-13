from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from models import ESGResponse
from services.esg_engine import compute_esg_metrics
from infrastructure.db.database import get_connection

router = APIRouter()


@router.get("/current", response_model=ESGResponse)
async def get_current_esg(machine_id: str = Query(..., description="Machine ID")):
    """
    Calculate current ESG/Carbon metrics for a machine
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Verify machine exists
        cur.execute("SELECT machine_id FROM machines WHERE machine_id = ?", (machine_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail=f"Machine {machine_id} not found")

        # Get latest measurements for ESG calculation
        cur.execute("""
            SELECT metric_key, metric_value
            FROM raw_measurements
            WHERE machine_id = ?
            ORDER BY timestamp DESC
            LIMIT 20
        """, (machine_id,))

        measurements = {row["metric_key"]: row["metric_value"] for row in cur.fetchall()}

        # Get previous total CO2eq
        cur.execute("""
            SELECT co2eq_total
            FROM esg_records
            WHERE machine_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (machine_id,))

        prev_row = cur.fetchone()
        prev_total = prev_row["co2eq_total"] if prev_row else 0.0

        # Compute ESG metrics
        esg_result = compute_esg_metrics(machine_id, measurements, prev_total)

        timestamp = datetime.utcnow()

        # Store ESG record
        cur.execute("""
            INSERT INTO esg_records (
                machine_id, timestamp, co2eq_instant, co2eq_total,
                fuel_rate_lh, kwh, scope
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            machine_id,
            timestamp.isoformat(),
            esg_result["co2eq_instant"],
            esg_result["co2eq_total"],
            esg_result.get("fuel_rate_lh"),
            esg_result.get("kwh"),
            esg_result["scope"]
        ))

        conn.commit()
        conn.close()

        return ESGResponse(
            machine_id=machine_id,
            timestamp=timestamp,
            co2eq_instant=esg_result["co2eq_instant"],
            co2eq_total=esg_result["co2eq_total"],
            fuel_rate_lh=esg_result.get("fuel_rate_lh"),
            kwh=esg_result.get("kwh"),
            scope=esg_result["scope"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{machine_id}")
async def get_esg_history(machine_id: str, limit: int = Query(default=100, le=500)):
    """
    Get ESG history for a machine
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT machine_id, timestamp, co2eq_instant, co2eq_total,
                   fuel_rate_lh, kwh, scope
            FROM esg_records
            WHERE machine_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (machine_id, limit))

        rows = cur.fetchall()
        conn.close()

        return {
            "machine_id": machine_id,
            "records": [dict(row) for row in rows]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_esg_summary():
    """
    Get aggregated ESG summary across all machines
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                m.machine_id,
                m.machine_type,
                m.site,
                COALESCE(MAX(e.co2eq_total), 0) as total_co2eq,
                COUNT(e.id) as measurement_count
            FROM machines m
            LEFT JOIN esg_records e ON m.machine_id = e.machine_id
            GROUP BY m.machine_id, m.machine_type, m.site
        """)

        machines = [dict(row) for row in cur.fetchall()]
        conn.close()

        total_emissions = sum(m["total_co2eq"] for m in machines)

        return {
            "total_co2eq_kg": total_emissions,
            "total_co2eq_tons": total_emissions / 1000,
            "machines_count": len(machines),
            "machines": machines
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
