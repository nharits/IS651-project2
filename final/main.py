# main.py - รวมทุกอย่างในไฟล์เดียว

from fastapi import FastAPI, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field
from typing import List, Optional, Generator
import sqlite3
from datetime import datetime, date

# -----------------------------------------------------------------
# 1. DB CONNECTION AND DEPENDENCY
# -----------------------------------------------------------------

# กำหนดชื่อฐานข้อมูล: ใช้เส้นทางแบบสัมบูรณ์ (Absolute Path)
# **** โค้ดที่ได้รับการแก้ไขตามที่คุณต้องการ ****
# DATABASE_URL = "/Users/harits/Documents/IS651lab/project2/final/metabase/metabase-data/garmin_clone.db" 
DATABASE_URL = "garmin_clone.db"
# **********************************************


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    ฟังก์ชัน Generator สำหรับสร้างและจัดการการเชื่อมต่อฐานข้อมูล
    ใช้ใน FastAPI ด้วยระบบ Dependency Injection
    """
    # เพิ่ม timeout เพื่อจัดการกรณีที่ฐานข้อมูลถูกล็อคโดย Metabase หรือ Process อื่น
    conn = sqlite3.connect(DATABASE_URL, timeout=10.0) 
    conn.row_factory = sqlite3.Row  # ทำให้ผลลัพธ์เป็น Row Object ที่เข้าถึงคอลัมน์ด้วยชื่อได้
    try:
        # เปิดใช้งาน Foreign Key Constraints สำหรับการเชื่อมต่อนี้
        conn.execute("PRAGMA foreign_keys = ON;")
        yield conn
    finally:
        conn.close()


# -----------------------------------------------------------------
# 2. การตั้งค่า FastAPI และ Pydantic Schemas
# -----------------------------------------------------------------
app = FastAPI(
    title="Garmin Clone BI/Operation API (Single File)",
    description="Basic FastAPI Endpoints for Student Project using SQLite DB.",
    version="1.0.0"
)

# A. Schemas พื้นฐานสำหรับการแสดงผล (Operation Task)
class User(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: str
    registration_date: date = Field(..., description="ISO8601 Date: YYYY-MM-DD")

class Activity(BaseModel):
    activity_id: int
    user_id: int
    activity_type: str = Field(..., alias="activity_type_name")
    start_datetime: datetime
    distance_km: Optional[float]
    calories_kcal: Optional[int]

# B. Schemas สำหรับ BI/Dashboard (Output)
class RegionalActivitySummary(BaseModel):
    region_name: str = Field(..., description="ชื่อภูมิภาค เช่น Central, North")
    total_distance_km: float
    total_activities: int
    top_city: Optional[str]

class TopUserSummary(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    total_distance_km: float

class MissionCompletionRate(BaseModel):
    mission_id: int
    mission_name: str
    activity_type: str
    total_completions: int
    difficulty: str

class WeightChangeSummary(BaseModel):
    user_id: int
    first_name: str
    initial_weight_kg: float = Field(..., alias="initial_weight")
    final_weight_kg: float = Field(..., alias="final_weight")
    weight_change_kg: float
    days_recorded: int

class DeviceCreate(BaseModel):
    user_id: int
    device_model: str = Field(..., description="เช่น 'Garmin Forerunner 970'")

class GoalUpdateStatus(BaseModel):
    new_status: str = Field(..., description="สถานะใหม่: 'active', 'completed', หรือ 'failed'")
    
class LatestBiometric(BaseModel):
    weight: Optional[float]
    height: Optional[float]
    heart_rate_avg: Optional[int]
    sleep_score: Optional[int]
    measured_at: datetime


# =================================================================
# 3. OPERATION TASKS (4 Endpoints - GET, POST, PUT, DELETE)
# =================================================================

# Case 1: GET - ดึงข้อมูลผู้ใช้ตามสถานะการยืนยัน
@app.get("/users/verified_status", response_model=List[User], summary="OP1: Get Users by Verification Status")
def get_users_by_verification(
    is_verified: bool = Query(..., description="True for verified users (1), False for unverified (0)"),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    ดึงรายชื่อผู้ใช้ทั้งหมดตามสถานะ 'user_verify' (0 หรือ 1).
    """
    verify_int = 1 if is_verified else 0
    query = """
    SELECT user_id, first_name, last_name, email, registration_date
    FROM users
    WHERE user_verify = ?
    """
    cursor = db.execute(query, (verify_int,))
    results = cursor.fetchall()
    return [User(**row) for row in results]

# Case 2: POST - สร้างอุปกรณ์ใหม่ให้กับผู้ใช้
@app.post("/devices/create", status_code=201, summary="OP2: Register a New Device")
def create_new_device(
    device_data: DeviceCreate,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    ลงทะเบียนอุปกรณ์ใหม่ (เช่น นาฬิกา) ให้กับผู้ใช้ที่ระบุ
    """
    user_check = db.execute("SELECT 1 FROM users WHERE user_id = ?", (device_data.user_id,)).fetchone()
    if not user_check:
        raise HTTPException(status_code=404, detail=f"User ID {device_data.user_id} not found.")

    try:
        current_time = datetime.now().isoformat()
        db.execute("""
            INSERT INTO devices(user_id, device_model, created_at) 
            VALUES (?, ?, ?)
        """, (device_data.user_id, device_data.device_model, current_time))
        db.commit()
        return {"message": "Device registered successfully", "device_model": device_data.device_model}
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

# Case 3: PUT - อัปเดตสถานะ Goal
@app.put("/goals/{goal_id}/status", summary="OP3: Update Goal Status")
def update_goal_status(
    goal_id: int,
    status_update: GoalUpdateStatus,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    อัปเดตสถานะของ Goal ที่กำหนดโดย Goal ID
    """
    if status_update.new_status not in ['active', 'completed', 'failed']:
        raise HTTPException(status_code=400, detail="Invalid status. Must be 'active', 'completed', or 'failed'.")
    
    try:
        cursor = db.execute("""
            UPDATE goals
            SET status = ?, end_dt = ? 
            WHERE goal_id = ?
        """, (status_update.new_status, date.today().isoformat(), goal_id))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Goal ID {goal_id} not found.")
            
        db.commit()
        return {"message": f"Goal {goal_id} status updated to {status_update.new_status} successfully."}
        
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

# Case 4: DELETE - ลบบันทึกกิจกรรม (เช่น ข้อมูลไม่ถูกต้อง)
@app.delete("/activities/{activity_id}", status_code=204, summary="OP4: Delete Activity Record")
def delete_activity_record(
    activity_id: int,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    ลบรายการบันทึกกิจกรรมออกกำลังกายที่ระบุโดย Activity ID (ใช้ DELETE)
    """
    try:
        cursor = db.execute("DELETE FROM activities WHERE activity_id = ?", (activity_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Activity ID {activity_id} not found.")
            
        db.commit()
        return
        
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

# =================================================================
# 4. BI/DASHBOARD - BUSINESS LEVEL (4 Endpoints)
# =================================================================

# Case 5: BI/Bus - GET: ภูมิภาคที่มีกิจกรรมรวมมากที่สุด
@app.get("/bi/regions/activity_ranking", response_model=List[RegionalActivitySummary], summary="BI-Bus1: Regional Activity Ranking")
def get_regional_activity_ranking(db: sqlite3.Connection = Depends(get_db)):
    """(Business Level) แสดงภาพรวมกิจกรรมทั้งหมด (ระยะทาง) จำแนกตามภูมิภาคของประเทศไทย"""
    region_case_statement = """
        CASE 
            WHEN T6.location_id BETWEEN 1 AND 18 THEN 'Central'
            WHEN T6.location_id BETWEEN 19 AND 33 THEN 'North'
            WHEN T6.location_id BETWEEN 34 AND 45 THEN 'South'
            WHEN T6.location_id BETWEEN 46 AND 60 THEN 'Northeast'
            WHEN T6.location_id BETWEEN 61 AND 68 THEN 'East'
            WHEN T6.location_id BETWEEN 69 AND 77 THEN 'West'
            ELSE 'Unknown'
        END
    """
    query = f"""
    WITH RegionalData AS (
        SELECT T1.distance_km, T6.city AS location_city, {region_case_statement} AS region_name
        FROM activities AS T1 INNER JOIN locations AS T6 ON T1.location_id = T6.location_id
        WHERE T1.distance_km IS NOT NULL
    ),
    RegionSummary AS (
        SELECT region_name, SUM(distance_km) AS total_distance_km, COUNT(*) AS total_activities
        FROM RegionalData GROUP BY region_name
    ),
    TopCityInRegion AS (
        SELECT region_name, location_city, COUNT(*) AS city_activity_count,
            ROW_NUMBER() OVER(PARTITION BY region_name ORDER BY COUNT(*) DESC) as rn
        FROM RegionalData GROUP BY region_name, location_city
    )
    SELECT
        T1.region_name, ROUND(T1.total_distance_km, 2) AS total_distance_km, T1.total_activities, T2.location_city AS top_city
    FROM RegionSummary AS T1 INNER JOIN TopCityInRegion AS T2 ON T1.region_name = T2.region_name
    WHERE T2.rn = 1 ORDER BY total_distance_km DESC;
    """
    cursor = db.execute(query)
    results = cursor.fetchall()
    return [RegionalActivitySummary(**row) for row in results]

# Case 6: BI/Bus - GET: อัตราการทำภารกิจสำเร็จตามความยาก
@app.get("/bi/missions/completion_rate", response_model=List[MissionCompletionRate], summary="BI-Bus2: Mission Completion Rate by Type")
def get_mission_completion_rate(db: sqlite3.Connection = Depends(get_db)):
    """(Business Level) วิเคราะห์ความนิยม/ความท้าทายของภารกิจ..."""
    query = """
    SELECT T1.mission_id, T1.name AS mission_name, T4.name AS activity_type, T3.name AS difficulty,
        COUNT(T2.user_id) AS total_completions
    FROM missions AS T1 INNER JOIN mission_completion AS T2 ON T1.mission_id = T2.mission_id
    INNER JOIN mission_difficulties AS T3 ON T1.mission_difficulty_id = T3.mission_difficulty_id
    INNER JOIN activity_types AS T4 ON T1.activity_type_id = T4.activity_type_id
    GROUP BY T1.mission_id, T1.name, T4.name, T3.name
    ORDER BY total_completions DESC, T3.mission_difficulty_id ASC LIMIT 10;
    """
    cursor = db.execute(query)
    return [MissionCompletionRate(**row) for row in cursor.fetchall()]

# Case 7: BI/Bus - GET: Top 10 ผู้ใช้ที่ทำกิจกรรมรวม (ระยะทาง) มากที่สุด
@app.get("/bi/users/top_distance", response_model=List[TopUserSummary], summary="BI-Bus3: Top 10 Distance Users")
def get_top_distance_users(db: sqlite3.Connection = Depends(get_db)):
    """(Business Level) จัดอันดับผู้ใช้ที่วิ่ง/ปั่นจักรยาน/เดิน..."""
    query = """
    SELECT T1.user_id, T2.first_name, T2.last_name, ROUND(SUM(T1.distance_km), 2) AS total_distance_km
    FROM activities AS T1 INNER JOIN users AS T2 ON T1.user_id = T2.user_id
    WHERE T1.activity_type_id BETWEEN 1 AND 6
    GROUP BY T1.user_id ORDER BY total_distance_km DESC LIMIT 10;
    """
    cursor = db.execute(query)
    return [TopUserSummary(**row) for row in cursor.fetchall()]

# Case 8: BI/Bus - GET: ข้อมูล Biometrics - การเปลี่ยนแปลงน้ำหนักเฉลี่ยตามผู้ใช้
@app.get("/bi/biometrics/weight_change", response_model=List[WeightChangeSummary], summary="BI-Bus4: User Weight Change (BI)")
def get_user_weight_change_summary(db: sqlite3.Connection = Depends(get_db)):
    """(Business Level) แสดงภาพรวมการเปลี่ยนแปลงน้ำหนักของผู้ใช้..."""
    query = """
    WITH RankedBiometrics AS (
        SELECT user_id, weight, measured_at,
            ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY measured_at ASC) as first_rn,
            ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY measured_at DESC) as last_rn,
            COUNT(*) OVER(PARTITION BY user_id) as total_records
        FROM biometrics WHERE weight IS NOT NULL
    ),
    WeightSummary AS (
        SELECT T1.user_id, T2.first_name, T2.last_name,
            (SELECT weight FROM RankedBiometrics WHERE user_id = T1.user_id AND first_rn = 1) AS initial_weight,
            (SELECT weight FROM RankedBiometrics WHERE user_id = T1.user_id AND last_rn = 1) AS final_weight,
            T1.total_records
        FROM RankedBiometrics AS T1 INNER JOIN users AS T2 ON T1.user_id = T2.user_id
        GROUP BY T1.user_id, T2.first_name, T2.last_name, T1.total_records
        HAVING T1.total_records >= 10
    )
    SELECT user_id, first_name, initial_weight, final_weight,
        ROUND(final_weight - initial_weight, 2) AS weight_change_kg,
        total_records AS days_recorded
    FROM WeightSummary ORDER BY weight_change_kg DESC;
    """
    cursor = db.execute(query)
    return [WeightChangeSummary(**row) for row in cursor.fetchall()]


# =================================================================
# 5. BI/DASHBOARD - USER LEVEL (4 Endpoints)
# =================================================================

# Case 9: BI/User - GET: สถิติกิจกรรมของผู้ใช้ตาม Activity Type
@app.get("/bi/user/{user_id}/activity_stats", response_model=List[Activity], summary="BI-User1: User Activity Feed")
def get_user_activity_feed(
    user_id: int = Path(..., description="ID ของผู้ใช้ที่ต้องการดึงข้อมูล"),
    limit: int = Query(10, ge=1, le=50, description="จำนวนกิจกรรมล่าสุดที่ต้องการดึง"),
    db: sqlite3.Connection = Depends(get_db)
):
    """(User Level) ดึงรายการกิจกรรมล่าสุดของผู้ใช้ที่กำหนด (Feed)"""
    if not db.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)).fetchone():
        raise HTTPException(status_code=404, detail=f"User ID {user_id} not found.")

    query = """
    SELECT T1.activity_id, T1.user_id, T2.name AS activity_type_name, T1.start_datetime, T1.distance_km, T1.calories_kcal
    FROM activities AS T1 INNER JOIN activity_types AS T2 ON T1.activity_type_id = T2.activity_type_id
    WHERE T1.user_id = ? ORDER BY T1.start_datetime DESC LIMIT ?
    """
    cursor = db.execute(query, (user_id, limit))
    return [Activity.model_validate(row).model_dump(by_alias=True) for row in cursor.fetchall()]


# Case 10: BI/User - GET: การแจ้งเตือนที่ยังไม่ได้อ่าน
@app.get("/bi/user/{user_id}/unread_notifications", summary="BI-User2: Unread Notifications Count")
def get_unread_notifications_count(
    user_id: int = Path(..., description="ID ของผู้ใช้"),
    db: sqlite3.Connection = Depends(get_db)
):
    """(User Level) ดึงจำนวนการแจ้งเตือนที่ผู้ใช้ยังไม่ได้อ่าน (is_read = 0)"""
    if not db.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)).fetchone():
        raise HTTPException(status_code=404, detail=f"User ID {user_id} not found.")

    query = """
    SELECT COUNT(*) AS unread_count
    FROM notification
    WHERE user_id = ? AND is_read = 0
    """
    cursor = db.execute(query, (user_id,))
    count = cursor.fetchone()["unread_count"]
    return {"user_id": user_id, "unread_notifications": count}


# Case 11: BI/User - GET: คะแนน Biometrics ล่าสุด
@app.get("/bi/user/{user_id}/latest_biometrics", response_model=LatestBiometric, summary="BI-User3: Latest Biometrics Score")
def get_latest_biometrics(
    user_id: int = Path(..., description="ID ของผู้ใช้"),
    db: sqlite3.Connection = Depends(get_db)
):
    """(User Level) ดึงข้อมูล Biometrics ล่าสุดที่บันทึกไว้สำหรับผู้ใช้รายนี้"""
    if not db.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)).fetchone():
        raise HTTPException(status_code=404, detail=f"User ID {user_id} not found.")

    query = """
    SELECT weight, height, heart_rate_avg, sleep_score, measured_at
    FROM biometrics
    WHERE user_id = ?
    ORDER BY measured_at DESC
    LIMIT 1
    """
    cursor = db.execute(query, (user_id,))
    result = cursor.fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="No biometrics data found for this user.")
        
    return LatestBiometric(**result)


# Case 12: BI/User - GET: สรุปสถานะ Goals ปัจจุบัน
@app.get("/bi/user/{user_id}/goal_summary", summary="BI-User4: Current Goal Summary")
def get_current_goal_summary(
    user_id: int = Path(..., description="ID ของผู้ใช้"),
    db: sqlite3.Connection = Depends(get_db)
):
    """(User Level) สรุปจำนวน Goals ที่สถานะ 'active', 'completed', และ 'failed' สำหรับผู้ใช้"""
    if not db.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)).fetchone():
        raise HTTPException(status_code=404, detail=f"User ID {user_id} not found.")

    query = """
    SELECT status, COUNT(*) AS count
    FROM goals
    WHERE user_id = ?
    GROUP BY status
    """
    cursor = db.execute(query, (user_id,))
    results = cursor.fetchall()
    
    summary = {
        'user_id': user_id,
        'active': 0,
        'completed': 0,
        'failed': 0
    }
    
    for row in results:
        status = row['status']
        count = row['count']
        if status in summary:
            summary[status] = count
            
    return summary