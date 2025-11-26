# api_service.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from typing import List, Optional, Dict, Any

# --- 1. CONFIGURATION ---
DB_PATH = "garmin_clone.db"

# --- 2. Pydantic Models for Data Validation (Input/Output) ---
# 2.1. Activity (GET Output)
class Activity(BaseModel):
    activity_id: int
    user_id: int
    activity_type_id: int
    start_datetime: str
    distance_km: Optional[float]
    calories_kcal: Optional[int]

# 2.2. Biometric (GET Output)
class Biometric(BaseModel):
    biometric_id: int
    user_id: int
    weight: Optional[float]
    height: Optional[float]
    heart_rate_avg: Optional[int]
    measured_at: str

# 2.3. New Biometric Data (POST Input)
class BiometricCreate(BaseModel):
    user_id: int
    weight: float
    height: float
    blood_pressure_avg: str # e.g., "120/80"
    heart_rate_avg: int
    sleep_score: int
    # ไม่ต้องระบุ measured_at, ให้ API สร้างเวลาปัจจุบันให้

# --- 3. DATABASE HELPER FUNCTIONS ---
def get_db_connection():
    """Returns a connection object to the SQLite database with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

# --- 4. FASTAPI APPLICATION SETUP ---
app = FastAPI(
    title="Garmin Clone Mock Data API",
    description="API for BI testing using Users, Activities, and Biometrics tables.",
    version="1.0.0"
)

# ----------------------------------------------------------------------
# A. OPERATION TASK APIs (GET, POST, DELETE)
# ----------------------------------------------------------------------

## 1. Activities Management (GET & DELETE)
@app.get("/activities/user/{user_id}", response_model=List[Activity], 
         summary="[GET] Get all activities for a specific user.")
async def get_user_activities(user_id: int):
    """
    ดึงรายการกิจกรรมทั้งหมดสำหรับผู้ใช้ที่ระบุ (จำกัด 100 รายการล่าสุด)
    """
    conn = get_db_connection()
    try:
        activities = conn.execute(
            """
            SELECT activity_id, user_id, activity_type_id, start_datetime, distance_km, calories_kcal
            FROM activities
            WHERE user_id = ?
            ORDER BY start_datetime DESC
            LIMIT 100
            """,
            (user_id,)
        ).fetchall()
        
        if not activities:
            raise HTTPException(status_code=404, detail=f"No activities found for user ID {user_id}")
            
        # แปลง sqlite.Row เป็น Dict เพื่อให้ Pydantic Model ใช้ได้
        return [dict(a) for a in activities]
    finally:
        conn.close()

@app.delete("/activities/{activity_id}", summary="[DELETE] Remove a specific activity.")
async def delete_activity(activity_id: int):
    """
    ลบกิจกรรมที่ระบุออกจากฐานข้อมูล
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activities WHERE activity_id = ?", (activity_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Activity ID {activity_id} not found.")
        conn.commit()
        return {"message": f"Activity ID {activity_id} deleted successfully."}
    finally:
        conn.close()

# ----------------------------------------------------------------------

## 2. Biometrics Management (POST & GET)
@app.post("/biometrics/add", summary="[POST] Add new biometric data for a user.")
async def create_biometric_data(data: BiometricCreate):
    """
    เพิ่มบันทึกไบโอเมตริกซ์ใหม่ (น้ำหนัก, HR, BP, คะแนนการนอน) สำหรับผู้ใช้
    """
    from datetime import datetime
    measured_at = datetime.utcnow().isoformat() # ใช้เวลานาฬิกาโลก ณ ปัจจุบัน
    
    conn = get_db_connection()
    try:
        # หา max(biometric_id) แล้ว +1
        max_id_result = conn.execute("SELECT MAX(biometric_id) FROM biometrics").fetchone()
        new_id = (max_id_result[0] or 0) + 1
        
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO biometrics (biometric_id, user_id, weight, weight_unit, height, height_unit, blood_pressure_avg, heart_rate_avg, sleep_score, measured_at)
            VALUES (?, ?, ?, 'kg', ?, 'cm', ?, ?, ?, ?)
            """,
            (new_id, data.user_id, data.weight, data.height, data.blood_pressure_avg, data.heart_rate_avg, data.sleep_score, measured_at)
        )
        conn.commit()
        return {"biometric_id": new_id, "user_id": data.user_id, "measured_at": measured_at, "message": "Biometric record created."}
    except sqlite3.IntegrityError:
         raise HTTPException(status_code=400, detail="User ID not found or data integrity issue.")
    finally:
        conn.close()

@app.get("/biometrics/user/{user_id}", response_model=List[Biometric], 
         summary="[GET] Get the 7 most recent biometric records for a user.")
async def get_latest_biometrics(user_id: int):
    """
    ดึงบันทึกไบโอเมตริกซ์ล่าสุด 7 รายการสำหรับผู้ใช้ที่ระบุ
    """
    conn = get_db_connection()
    try:
        biometrics = conn.execute(
            """
            SELECT biometric_id, user_id, weight, height, heart_rate_avg, measured_at
            FROM biometrics
            WHERE user_id = ?
            ORDER BY measured_at DESC
            LIMIT 7
            """,
            (user_id,)
        ).fetchall()
        
        if not biometrics:
            raise HTTPException(status_code=404, detail=f"No biometrics found for user ID {user_id}")
            
        return [dict(b) for b in biometrics]
    finally:
        conn.close()

# ----------------------------------------------------------------------

## 3. User & High-Level Metrics (GET & GET)
@app.get("/users/{user_id}/summary", summary="[GET] Get user details and top-level metrics.")
async def get_user_summary(user_id: int):
    """
    ดึงข้อมูลผู้ใช้ (ชื่อ, วันเกิด) และสถิติสรุปกิจกรรม (ระยะทางรวม, แคลอรี่รวม)
    """
    conn = get_db_connection()
    try:
        # 1. User Info
        user = conn.execute(
            "SELECT user_id, first_name, last_name, user_birthday FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User ID {user_id} not found.")

        # 2. Aggregated Metrics
        metrics = conn.execute(
            """
            SELECT 
                SUM(distance_km) AS total_distance_km,
                SUM(calories_kcal) AS total_calories_kcal
            FROM activities
            WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()

        return {
            "user_info": dict(user),
            "activity_metrics": {
                "total_distance_km": round(metrics['total_distance_km'], 2) if metrics['total_distance_km'] else 0.0,
                "total_calories_kcal": int(metrics['total_calories_kcal']) if metrics['total_calories_kcal'] else 0,
            }
        }
    finally:
        conn.close()

@app.get("/users/top_cities", summary="[GET] Get the top 5 cities with the most active users.")
async def get_top_active_cities():
    """
    ดึง 5 อันดับแรกของเมืองที่มีผู้ใช้งานมากที่สุด (อิงจาก Home Location ในตาราง Users)
    """
    conn = get_db_connection()
    try:
        # ตรรกะ: เนื่องจากใน populate_mock_data.py เราไม่ได้เก็บ base_location_id ในตาราง users
        # แต่มีการสร้าง location_id 1-N_LOCATIONS ตามลำดับใน THAI_CITIES_ORDERED
        # เราจะใช้ location_id 1-77 เป็น Location ID ของ Home City
        # แต่เนื่องจากไม่มี column นั้นใน DDL, เราจะใช้ตาราง activities แทน:
        
        # NOTE: การใช้ตาราง activities จะนับตามกิจกรรมที่เกิดขึ้นใน Location นั้น
        top_cities = conn.execute(
            """
            SELECT 
                l.city, 
                COUNT(a.activity_id) AS total_activities
            FROM activities a
            JOIN locations l ON a.location_id = l.location_id
            GROUP BY l.city
            ORDER BY total_activities DESC
            LIMIT 5
            """
        ).fetchall()

        return [dict(c) for c in top_cities]
    finally:
        conn.close()

# ----------------------------------------------------------------------
# B. RECHECK APIs (สำหรับทดสอบ Operation Task A)
# ----------------------------------------------------------------------

## 1. Recheck: Activity Data Integrity
@app.get("/recheck/activity_count/{user_id}", summary="[RECHECK] Count total activities for a user.")
async def recheck_activity_count(user_id: int):
    """
    นับจำนวนกิจกรรมทั้งหมดสำหรับผู้ใช้ที่ระบุ
    """
    conn = get_db_connection()
    try:
        count = conn.execute(
            "SELECT COUNT(activity_id) FROM activities WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]
        return {"user_id": user_id, "total_activities": count}
    finally:
        conn.close()

## 2. Recheck: Biometric Data Status
@app.get("/recheck/biometric_count/{user_id}", summary="[RECHECK] Count total biometric records for a user.")
async def recheck_biometric_count(user_id: int):
    """
    นับจำนวนบันทึกไบโอเมตริกซ์ทั้งหมดสำหรับผู้ใช้ที่ระบุ
    """
    conn = get_db_connection()
    try:
        count = conn.execute(
            "SELECT COUNT(biometric_id) FROM biometrics WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]
        return {"user_id": user_id, "total_biometric_records": count}
    finally:
        conn.close()

## 3. Recheck: Total User Count
@app.get("/recheck/total_users", summary="[RECHECK] Get total number of users in the system.")
async def recheck_total_users():
    """
    นับจำนวนผู้ใช้ทั้งหมดในตาราง Users
    """
    conn = get_db_connection()
    try:
        count = conn.execute("SELECT COUNT(user_id) FROM users").fetchone()[0]
        return {"total_users": count}
    finally:
        conn.close()