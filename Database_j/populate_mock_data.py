# populate_mock_data.py
"""
Populate garmin_clone.db with realistic mock data for BI testing.
Usage:
    python populate_mock_data.py
Adjust N_USERS, N_ACTIVITIES, etc. Comments explain how generation works.
"""
import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker

# Configuration: change counts for larger/smaller datasets
N_USERS = 500            # number of users
N_LOCATIONS = 77         # locations
N_ACTIVITIES = 100000    # REVISED: activity records (50000 -> 100000)
N_COMMUNITIES = 50       # REVISED: (20 -> 50)
N_EVENTS = 250           # REVISED: (80 -> 250)
N_GOALS = 2500           # REVISED: (750 -> 2500)
N_BIOMETRICS = 15000     # (Keep)
N_DEVICES = 600          # (Keep)
N_NOTIFICATIONS = 15000  # (Keep)
N_NEWS = 100             # REVISED: (30 -> 100)
N_ACHIEVEMENTS = 5000    # REVISED: (2500 -> 5000)
N_MISSIONS = 50          # REVISED: (25 -> 50)
N_USER_MISSIONS = 45000  # NEW: Target number of mission completion records (Max unique pairs is 25,000 based on N_USERS=500, N_MISSIONS=50)
DB_PATH = "garmin_clone.db"
# เพิ่มในส่วน Configuration ด้านบน (พร้อมกับ N_USERS, N_ACTIVITIES, ฯลฯ)
DAYS_HISTORY = 30        # For biometrics: collect one record per user per day for this many days (Keep)
N_REGIONS = 6            # N_REGIONS = 6 ภูมิภาคหลัก

# 1. รายการจังหวัดของไทย 77 จังหวัด (พร้อมพิกัดตัวอย่าง) เรียงตามภูมิภาค
# หมายเหตุ: นี่คือชุดข้อมูลที่กำหนดขึ้นเพื่อจำลองการเรียงตามภูมิศาสตร์ 
# Location ID จะถูกกำหนดตามลำดับในลิสต์นี้
THAI_CITIES_ORDERED = [
    # ภาคกลาง (Central: Location ID 1-18) - 18 จังหวัด
    ('Bangkok', 13.75, 100.5), ('Nonthaburi', 13.88, 100.52), ('Samut Prakan', 13.59, 100.59), 
    ('Pathum Thani', 14.02, 100.53), ('Ayutthaya', 14.35, 100.57), ('Saraburi', 14.53, 100.91), 
    ('Lopburi', 14.8, 100.67), ('Sing Buri', 14.88, 100.38), ('Ang Thong', 14.58, 100.47), 
    ('Chai Nat', 15.18, 100.12), ('Nakhon Sawan', 15.79, 100.12), ('Phichit', 16.27, 100.35), 
    ('Kamphaeng Phet', 16.48, 99.52), ('Uthai Thani', 15.38, 100.03), ('Suphan Buri', 14.47, 100.02), 
    ('Nakhon Pathom', 13.82, 100.07), ('Samut Sakhon', 13.55, 100.27), ('Samut Songkhram', 13.4, 99.98),

    # ภาคเหนือ (North: Location ID 19-33) - 15 จังหวัด
    ('Chiang Mai', 18.78, 98.98), ('Chiang Rai', 19.9, 99.82), ('Lamphun', 18.57, 99.01), 
    ('Lampang', 18.29, 99.5), ('Phrae', 18.15, 100.15), ('Nan', 18.78, 100.78), 
    ('Phayao', 19.18, 99.88), ('Dara', 16.75, 99.28), ('Mae Hong Son', 19.3, 97.97), 
    ('Sukhothai', 17.0, 99.82), ('Pitsanulok', 16.8, 100.25), ('Phetchabun', 16.15, 101.15), 
    ('Utaradit', 17.62, 100.1), ('Tak', 16.87, 99.12), ('Nakhon Thai', 18.13, 100.12), 
    
    # ภาคใต้ (South: Location ID 34-45) - 12 จังหวัด
    ('Phuket', 7.88, 98.39), ('Krabi', 8.08, 98.91), ('Songkhla', 7.2, 100.6), 
    ('Surat Thani', 9.14, 99.33), ('Nakhon Si Thammarat', 8.44, 99.96), ('Trang', 7.55, 99.61), 
    ('Phatthalung', 7.61, 100.07), ('Yala', 6.55, 101.27), ('Pattani', 6.87, 101.25), 
    ('Narathiwat', 6.43, 101.83), ('Satun', 6.6, 100.0), ('Ranong', 9.97, 98.63), 

    # ภาคตะวันออกเฉียงเหนือ (Northeast: Location ID 46-60) - 15 จังหวัด
    ('Nakhon Ratchasima', 14.97, 102.08), ('Khon Kaen', 16.43, 102.83), ('Udon Thani', 17.38, 102.78), 
    ('Ubon Ratchathani', 15.22, 104.87), ('Surin', 14.88, 103.5), ('Buriram', 15.1, 103.1), 
    ('Si Sa Ket', 15.11, 104.31), ('Roi Et', 16.05, 103.65), ('Kalasin', 16.43, 103.5), 
    ('Maha Sarakham', 16.18, 103.3), ('Yasothon', 15.82, 104.13), ('Mukdahan', 16.55, 104.7), 
    ('Chaiyaphum', 15.8, 102.03), ('Amnat Charoen', 15.87, 105.0), ('Nong Khai', 17.88, 102.75), 
    
    # ภาคตะวันออก (East: Location ID 61-68) - 8 จังหวัด
    ('Chonburi', 13.36, 100.98), ('Rayong', 12.67, 101.27), ('Chanthaburi', 12.61, 102.1), 
    ('Trat', 12.23, 102.51), ('Sa Kaeo', 13.83, 102.0), ('Prachinburi', 14.07, 101.38), 
    ('Chachoengsao', 13.6, 101.12), ('Nakhon Nayok', 14.2, 101.18),
    
    # ภาคตะวันตก (West: Location ID 69-77) - 9 จังหวัด (เพื่อรวมให้ครบ 77)
    ('Kanchanaburi', 14.0, 99.5), ('Phetchaburi', 13.1, 99.94), ('Ratchaburi', 13.52, 99.82), 
    ('Prachuap Khiri Khan', 11.83, 99.78), ('Tak (West)', 16.87, 99.12), ('Phetchabun (West)', 16.15, 101.15),
    ('Loei', 17.48, 101.78), ('Nong Bua Lamphu', 17.2, 102.42), ('Bueng Kan', 18.36, 103.65),
    
    # รวม 18 + 15 + 12 + 15 + 8 + 9 = 77 Provinces
]

# กำหนดช่วง ID ของ Location ในแต่ละภูมิภาค
# Region ID (1-6) จะอ้างอิงลำดับ ID ที่ใส่ในตาราง locations
REGION_MAPPING = {
    1: list(range(1, 19)),     # Region 1: ภาคกลาง (Central)
    2: list(range(19, 34)),    # Region 2: ภาคเหนือ (North)
    3: list(range(34, 46)),    # Region 3: ภาคใต้ (South)
    4: list(range(46, 61)),    # Region 4: ภาคตะวันออกเฉียงเหนือ (Northeast)
    5: list(range(61, 69)),    # Region 5: ภาคตะวันออก (East)
    6: list(range(69, N_LOCATIONS + 1)) # Region 6: ภาคตะวันตก (West)
}

# List of tables to clear to ensure the script is idempotent (can be re-run)
TABLES_TO_CLEAR = [
    'genders', 'mission_difficulties', 'activity_types', 'locations', 'users',
    'devices', 'activities', 'communities', 'communities_users', 'events',
    'event_participants', 'goals', 'biometrics', 'notification', 'news',
    'achievements', 'missions', 'mission_completion' # <<< แก้ไข: เพิ่ม mission_completion >>>
]

fake = Faker()
Faker.seed(1)
random.seed(1)

def iso_days_ago(days):
    return (datetime.utcnow() - timedelta(days=days)).isoformat()

def rand_between_dates(start_days_ago, end_days_ago):
    start = datetime.utcnow() - timedelta(days=start_days_ago)
    end = datetime.utcnow() - timedelta(days=end_days_ago)
    return fake.date_time_between(start_date=start, end_date=end).isoformat()

# เพิ่มฟังก์ชันนี้หลัง rand_between_dates ในส่วนบนของไฟล์
def rand_realistic_datetime(start_days_ago, end_days_ago, start_hour, end_hour):
    """Generates a random datetime within a day range and an hour range."""
    
    # 1. Determine the date (สามารถเป็นอดีตหรืออนาคต)
    start_date = datetime.utcnow().date() - timedelta(days=start_days_ago)
    end_date = datetime.utcnow().date() - timedelta(days=end_days_ago)
    
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    days_diff = (end_date - start_date).days
    random_date = start_date + timedelta(days=random.randint(0, days_diff))

    # 2. Determine the time
    actual_hour = random.randint(start_hour, end_hour)
    random_minute = random.randint(0, 59)
    random_second = random.randint(0, 59)

    return datetime(random_date.year, random_date.month, random_date.day,
                    actual_hour, random_minute, random_second).isoformat()


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Ensure foreign_keys on
    cur.execute("PRAGMA foreign_keys = ON;")

    # === DDL: MISSION COMPLETION TABLE (เพิ่มใหม่เพื่อให้ตารางมีอยู่ก่อนล้าง/ใส่ข้อมูล) ===
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mission_completion (
            user_id                 INTEGER NOT NULL,
            mission_id              INTEGER NOT NULL,
            completed_at            TEXT NOT NULL,
            is_rewarded             INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY (user_id, mission_id), 
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (mission_id) REFERENCES missions(mission_id) ON DELETE CASCADE
        );
    """)
    # ===============================================================================

    # 0) NEW: Clear data from all tables to allow re-running the script
    print("Clearing existing mock data...")
    
    # ใช้ reversed() เพื่อลบตารางลูกก่อนตารางแม่
    for table in reversed(TABLES_TO_CLEAR):
        try:
            # ใช้ 'DELETE FROM' เพื่อล้างข้อมูลในตาราง
            cur.execute(f"DELETE FROM {table}")
        except sqlite3.OperationalError:
            pass # Ignore if a table does not exist yet

    conn.commit()
    print("Existing data cleared successfully.")

    # 1) Fill lookup tables: genders, mission_difficulties, activity_types
    genders = ['male', 'female', 'non-binary', 'prefer not to say']
    for i, g in enumerate(genders, start=1):
        cur.execute("INSERT INTO genders(gender_id,name) VALUES(?,?)", (i,g))

    # MISSION DIFFICULTIES
    # เพิ่ม 'extreme' เพื่อให้ครบ 4 ระดับ ตาม logic การให้รางวัลใหม่
    mission_diff = ['easy','medium','hard','extreme']
    for i, m in enumerate(mission_diff, start=1):
        cur.execute("INSERT INTO mission_difficulties(mission_difficulty_id,name) VALUES(?,?)", (i,m))

    activity_types = [
        # ID 1-6: กิจกรรมที่มีระยะทางเป็นหลัก (Distance-based)
        'Run',              # 1: วิ่ง
        'Walk',             # 2: เดิน
        'Cycling',          # 3: ปั่นจักรยาน
        'Hike',             # 4: เดินป่า
        'Swim',             # 5: ว่ายน้ำ
        'Rowing',           # 6: พายเรือ/กรรเชียงบก
        
        # ID 7-10: กิจกรรมที่เน้นความแข็งแรง/ใช้เวลา (Time/Strength-based)
        'Strength Training',# 7: ฝึกความแข็งแรง/ยกน้ำหนัก
        'Yoga / Pilates',   # 8: โยคะ, พิลาทิส
        'Hiit / Functional',# 9: ฝึกความเข้มข้นสูงและฟังก์ชัน
        'Dance / Aerobics'  # 10: เต้น, แอโรบิก, ซุมบ้า
    ]
    
    for i, a in enumerate(activity_types, start=1):
        cur.execute("INSERT INTO activity_types(activity_type_id,name) VALUES(?,?)", (i,a))

    # 2) Locations
    
    # REVISED: Insert 77 Thai provinces ordered by region for realistic grouping
    loc_id = 1
    for city_name, lat, lon in THAI_CITIES_ORDERED:
        # ใช้ city_name จาก THAI_CITIES_ORDERED
        cur.execute("INSERT INTO locations(location_id, city, location_latitude, location_longitude) VALUES(?,?,?,?)",
                    (loc_id, city_name, lat, lon))
        loc_id += 1
        
        # ถ้า N_LOCATIONS ถูกตั้งไว้น้อยกว่า 77 หรือต้องการหยุดที่จำนวนที่กำหนด
        if loc_id > N_LOCATIONS:
            break

    # 3) Users
    print(f"Populating {N_USERS} users (Weighted Age Distribution: 15-80)...")
    user_ids = []

    # --- NEW LOGIC START: Weighted Age Distribution Setup ---
    AGE_WEIGHTS = [
        {'min_age': 25, 'max_age': 49, 'weight': 65},  # 65% Working Age (Highest)
        {'min_age': 15, 'max_age': 24, 'weight': 25},  # 25% Young Adults/Teens
        {'min_age': 50, 'max_age': 60, 'weight': 10},  # 10% Older Adults/Elderly (Lowest)
    ]
    AGE_RANGES = [item for item in AGE_WEIGHTS]
    WEIGHTS = [item['weight'] for item in AGE_WEIGHTS]
    # --- NEW LOGIC END ---

    for uid in range(1, N_USERS+1):
        gender_id = random.randint(1, len(genders))
        first = fake.first_name()
        last = fake.last_name()
        username = (first + last + str(random.randint(1,999))).lower()
        email = username + "@example.com"
        phone = fake.msisdn()[:12]
        
        # Registration date: ใช้ logic เดิม (rand_realistic_datetime)
        registration_date = rand_realistic_datetime(800, 0, start_hour=6, end_hour=23)
        
        # >>> REVISED BDAY GENERATION: ใช้ Weighted Random เพื่อเลือกช่วงอายุ <<<
        
        # 1. สุ่มเลือกช่วงอายุตามน้ำหนักที่กำหนด (65/25/10)
        selected_range = random.choices(AGE_RANGES, weights=WEIGHTS, k=1)[0]
        
        # 2. Generate วันเกิด (bday) ภายในช่วงอายุที่สุ่มได้
        min_age = selected_range['min_age']
        max_age = selected_range['max_age']
        
        # ใช้ Faker generate bday ภายในช่วง min_age ถึง max_age
        bday = fake.date_of_birth(minimum_age=min_age, maximum_age=max_age).isoformat()
        
        # <<< สิ้นสุดการแก้ไข BDAY >>>
        
        is_active = 1 if random.random() > 0.05 else 0
        user_verify = 1 if random.random() > 0.2 else 0

        cur.execute("""INSERT INTO users(user_id, gender_id, first_name, last_name, username, email, phone_number, user_verify, registration_date, user_birthday, is_active)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                    (uid, gender_id, first, last, username, email, phone, user_verify, registration_date, bday, is_active))
        user_ids.append(uid)

    # -------------------------------------------------------------
    # โค้ด Base Location ของผู้ใช้ (ต้องคงไว้เพื่อใช้ใน Activities)
    # -------------------------------------------------------------
    user_base_locations = {}
    location_list = list(range(1, N_LOCATIONS + 1))
    
    for uid in user_ids:
        # กำหนด Location ID (จังหวัด) แบบสุ่มให้เป็น Home Location ของ User นั้นๆ
        user_base_locations[uid] = random.choice(location_list)
    # -------------------------------------------------------------

    # 4) Devices (some users have devices)
    
    # NEW: รุ่นนาฬิกา Garmin ที่เป็นปัจจุบันและได้รับความนิยมในตลาด (พ.ย. 2025)
    device_models = [
        # Forerunner Series (Running/Triathlon)
        'Garmin Forerunner 970',
        'Garmin Forerunner 965',
        'Garmin Forerunner 570',
        'Garmin Forerunner 265',
        'Garmin Forerunner 165',
        'Garmin Forerunner 55',      # Entry-level running
        
        # Fenix/Epix Series (Premium Multisport/Outdoor)
        'Garmin Fenix 8 Pro',
        'Garmin Fenix 7 Pro',
        'Garmin Epix Gen 2',
        'Garmin Epix Pro (Gen 2)',
        'Garmin Enduro 3',           # Ultraperformance
        'Garmin tactix 8',           # Tactical
        
        # Venu/Vivoactive Series (Lifestyle/Health/Smartwatch)
        'Garmin Venu 4',
        'Garmin Venu X1',
        'Garmin Venu 3',
        'Garmin Vivoactive 6',
        'Garmin Vivoactive 5',
        'Garmin Lily 2',             # Fashion/Small form factor
        
        # Instinct Series (Rugged/Outdoor)
        'Garmin Instinct 3',
        'Garmin Instinct 2X Solar',
        'Garmin Instinct 2X Solar',
        'Garmin Instinct Crossover'
    ]
    
    device_id = 1
    
    for _ in range(N_DEVICES):
        user_id = random.choice(user_ids)
        model = random.choice(device_models)
        
        # ใช้ created_at ที่ถูกแก้ไขให้สมจริงแล้ว (6 AM - 11 PM)
        created_at = rand_realistic_datetime(800, 0, start_hour=6, end_hour=23)
        
        cur.execute("INSERT INTO devices(device_id, user_id, device_model, created_at) VALUES(?,?,?,?)",
                    (device_id, user_id, model, created_at))
        device_id += 1

   # 5) Activities (ตรรกะเวลาสอดคล้องกับกิจกรรม ถูกกำหนดไว้เฉพาะแล้ว)
    activity_id = 1
    
    # --------------------------------------------------------------------------------------
    # >>> NEW: Setup Region Lookups (ต้องทำก่อนลูป Activities) <<<
    # --------------------------------------------------------------------------------------
    location_regions = {}
    region_to_locations = {rid: [] for rid in REGION_MAPPING.keys()}

    for rid, loc_id_list in REGION_MAPPING.items():
        for loc_id in loc_id_list:
            if loc_id <= N_LOCATIONS: 
                location_regions[loc_id] = rid
                region_to_locations[rid].append(loc_id)
    # --------------------------------------------------------------------------------------

    # ใช้นโยบายการกำหนดค่าขอบเขตสูงสุดที่ปลอดภัยที่สุด
    max_device_id_to_link = max(1, device_id - 1) 
    
    for _ in range(N_ACTIVITIES):
        user_id = random.choice(user_ids)
        activity_type_id = random.randint(1, len(activity_types)) # สุ่มจากประเภทกิจกรรม 1-10

        # --------------------------------------------------------------------------------------
        # >>> REVISED: Logic การกำหนด location_id 70% Home / 20% Local / 10% Global (ตามภูมิศาสตร์) <<<
        # --------------------------------------------------------------------------------------
        
        # 1. ดึง Base Location ของ User และ Region
        base_loc_id = user_base_locations[user_id]
        base_region_id = location_regions[base_loc_id] # ดึง Region ID ที่สร้างไว้

        # 2. กำหนด Location ID ด้วยน้ำหนัก: 70% Home / 20% Local / 10% Global
        rand_weight = random.random()
        
        if rand_weight < 0.7:
            # 70% - Home Location (กิจกรรมส่วนใหญ่ในพื้นที่หลัก)
            loc_id = base_loc_id
        elif rand_weight < 0.9: # 0.7 + 0.2 = 0.9
            # 20% - Local Travel (สุ่มใน Location ใน Region เดียวกัน)
            current_region_locations = region_to_locations[base_region_id]
            
            # กรอง Home Location ออกจากการสุ่ม Local Travel
            local_options = [lid for lid in current_region_locations if lid != base_loc_id]
            
            if local_options:
                # สุ่มจากจังหวัดใกล้เคียง (ใน Region เดียวกัน)
                loc_id = random.choice(local_options)
            else:
                # กรณีมี Location เดียวใน Region หรือเกิดข้อผิดพลาด ให้กลับไปใช้ Home
                loc_id = base_loc_id
        else:
            # 10% - Global Travel (สุ่ม Location ID ทั่วประเทศ)
            loc_id = random.randint(1, N_LOCATIONS)
            
        # --------------------------------------------------------------------------------------
        # >>> สิ้นสุดการแก้ไข Location ID <<<

        device_ref = random.randint(1, max_device_id_to_link)

        # 1. กำหนดระยะเวลา (duration_min) ตาม Activity Type ให้เหมาะสม
        if activity_type_id in [1, 2, 4, 6, 10]: # Run, Walk, Hike, Rowing, Dance/Aerobics
            # ระยะเวลาปานกลางถึงยาว: 20 - 120 นาที
            duration_min = random.randint(20, 120)
        elif activity_type_id == 3: # Cycling
            # ระยะเวลายาว: 60 - 180 นาที
            duration_min = random.randint(60, 180)
        elif activity_type_id in [7]: # Strength Training
            # ระยะเวลาที่กำหนด: 45 - 90 นาที
            duration_min = random.randint(45, 90)
        elif activity_type_id in [8]: # Yoga / Pilates
            # ระยะเวลาที่กำหนด: 30 - 90 นาที
            duration_min = random.randint(30, 90)
        elif activity_type_id in [9]: # Hiit / Functional
            # ระยะเวลาสั้น: 15 - 60 นาที
            duration_min = random.randint(15, 60)
        else: # Swim (5)
            # ระยะเวลาปานกลาง: 30 - 90 นาที
            duration_min = random.randint(30, 90)

        # 2. คำนวณ start_datetime และ end_datetime ที่สอดคล้องกับเวลาจริงของมนุษย์
        
        # 2a. กำหนดวันที่ในอดีต (ไม่เกิน 365 วัน)
        date_of_activity = datetime.utcnow().date() - timedelta(days=random.randint(0, 365))
        
        # 2b. กำหนดช่วงชั่วโมงที่เหมาะสม
        if activity_type_id in [1, 2, 3, 4, 5, 6]: # กิจกรรมกลางแจ้ง/น้ำ (Run, Walk, Cycle, Hike, Swim, Rowing)
            # 5 AM ถึง 9 PM (เพื่อความปลอดภัยและแสงสว่าง)
            start_hour_min = 5 
            end_hour_max = 21 # 21:00 น.
        else: # กิจกรรมในร่ม/สตูดิโอ (Strength, Yoga, Hiit, Dance)
            # 6 AM ถึง 11 PM
            start_hour_min = 6
            end_hour_max = 23 # 23:00 น.

        # 2c. คำนวณชั่วโมงเริ่มต้นที่ปลอดภัย (Start Hour)
        max_duration_hours = duration_min / 60
        # ชั่วโมงที่ช้าที่สุดที่กิจกรรมสามารถเริ่มได้
        latest_safe_start_hour = end_hour_max - int(max_duration_hours)

        # สุ่มชั่วโมงเริ่มต้นจริง (ต้องอยู่ระหว่าง start_hour_min ถึง latest_safe_start_hour)
        actual_start_hour = random.randint(start_hour_min, max(start_hour_min, latest_safe_start_hour))
        
        random_minute = random.randint(0, 59)
        random_second = random.randint(0, 59)

        # start_dt: รวมวันที่ในอดีตกับชั่วโมงเริ่มต้นที่สุ่มมา
        start_dt = datetime(date_of_activity.year, date_of_activity.month, date_of_activity.day,
                            actual_start_hour, random_minute, random_second)
        
        # end_dt: คำนวณ end time
        end_dt = start_dt + timedelta(minutes=duration_min)

        # --- NEW LOGIC START: การคำนวณ Distance และ Calories ตาม ID 1-10 (รวมการปรับปรุงก่อนหน้านี้) ---

        distance = 0.0 # ตั้งค่าเริ่มต้น distance เป็น 0.0 เสมอ
        calories = 0
        
        # 1. กิจกรรมที่เน้นระยะทางเป็นหลัก (ID 1 ถึง 6)
        if activity_type_id in [1, 2, 3, 4, 5, 6]:
            
             # กำหนดค่าเฉลี่ยตาม ID (Run, Walk, Cycle, Hike, Swim, Rowing)
             # (avg_dist_km, dist_dev, cal_per_km)
             if activity_type_id == 1: # Run
                  # วิ่ง: ระยะปานกลาง, เผาผลาญสูง
                  avg_dist, dist_dev, cal_per_km = 6, 3, random.uniform(80, 100)
             elif activity_type_id == 2: # Walk
                  # เดิน: ระยะสั้นถึงปานกลาง, เผาผลาญต่ำ
                  avg_dist, dist_dev, cal_per_km = 4, 2, random.uniform(50, 70)
             elif activity_type_id == 3: # Cycling
                  # ปั่นจักรยาน: ระยะทางสูง, เผาผลาญต่ำ
                  avg_dist, dist_dev, cal_per_km = 25, 10, random.uniform(30, 60)
             elif activity_type_id == 5: # Swim
                  # ว่ายน้ำ: ระยะทางต่ำ, เผาผลาญสูงมาก
                  avg_dist, dist_dev, cal_per_km = 1.5, 0.5, random.uniform(90, 120)
             else: # Hike (4), Rowing (6) (ค่ากลาง)
                  avg_dist, dist_dev, cal_per_km = 4, 2, random.uniform(60, 90)
             
             # คำนวณระยะทางแบบ Gaussian และคำนวณแคลอรี่ตามระยะทาง
             distance = round(max(0.1, random.gauss(avg_dist, dist_dev)), 2)
             calories = int(max(100, distance * cal_per_km))

        # 2. กิจกรรมที่เน้นเวลา/ความแข็งแรง (ID 7 ถึง 10)
        elif activity_type_id in [7, 8, 9, 10]:
             
             distance = 0.0 # ตั้งระยะทางเป็น 0 สำหรับกิจกรรม Time-based
             
             # กำหนดอัตราการเผาผลาญตาม ID (kcal/นาที)
             if activity_type_id == 9: # Hiit / Functional (เผาผลาญสูงมาก)
                  cal_per_min = random.uniform(8, 13)
             elif activity_type_id == 7: # Strength Training (เผาผลาญสูง)
                  cal_per_min = random.uniform(6, 10)
             elif activity_type_id == 10: # Dance / Aerobics (เผาผลาญปานกลางค่อนข้างสูง)
                  cal_per_min = random.uniform(5, 9)
             else: # Yoga / Pilates (8) (เผาผลาญต่ำ)
                  cal_per_min = random.uniform(3, 6)
                  
             # คำนวณแคลอรี่ตามระยะเวลา (duration_min)
             calories = int(max(50, duration_min * cal_per_min))
        
        # 3. ตรวจสอบแคลอรี่ขั้นต่ำเพื่อป้องกันค่าต่ำเกินไป
        calories = max(50, calories)

        # --- NEW LOGIC END ---
        
        # 3. กำหนด created_at และ updated_at ให้สมจริง (ต้องเกิดขึ้นหลัง start_dt และก่อน end_dt)
        
        # created_at: บันทึกข้อมูลหลังกิจกรรมเริ่ม (1-10 นาทีหลัง start_dt)
        created_at_dt = start_dt + timedelta(minutes=random.randint(1, 10))
        
        # updated_at: อาจเกิดขึ้นหรือไม่ก็ได้ (ถ้ามีการแก้ไข) -> สุ่มให้เกิด 50%
        if random.random() > 0.5:
             # อัปเดตหลัง created_at และก่อน end_dt เล็กน้อย
             update_offset = random.randint(5, duration_min)
             updated_at_dt = created_at_dt + timedelta(minutes=update_offset)
             # ตรวจสอบให้ updated_at ไม่เลย end_dt
             updated_at_dt = min(updated_at_dt, end_dt)
        else:
             updated_at_dt = created_at_dt # ถ้าไม่มีการอัปเดต updated_at = created_at

        is_verified = 1 if random.random() > 0.3 else 0
        
        cur.execute("""INSERT INTO activities(activity_id, user_id, activity_type_id, location_id, device_id, start_datetime, end_datetime, distance_km, calories_kcal, is_verified, created_at, updated_at)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (activity_id, user_id, activity_type_id, loc_id, device_ref, 
                     start_dt.isoformat(), end_dt.isoformat(), distance, calories, is_verified, 
                     created_at_dt.isoformat(), updated_at_dt.isoformat()))
        activity_id += 1

    # 6) Communities and community users
    for cid in range(1, N_COMMUNITIES+1):
        location_id = random.randint(1, N_LOCATIONS)
        name = f"{random.choice(['Runners','Cyclists','Hikers','Swimmers'])} Group {cid}"
        description = fake.sentence(nb_words=8)
        # REVISED: ใช้ rand_realistic_datetime
        created_at = rand_realistic_datetime(800, 0, start_hour=6, end_hour=23)
        cur.execute("INSERT INTO communities(community_id, location_id, name, description, is_public, created_at) VALUES(?,?,?,?,?,?)",
                    (cid, location_id, name, description, 1 if random.random()>0.1 else 0, created_at))
        # members
        members = random.sample(user_ids, k=max(3, random.randint(5, 40)))
        for u in members:
            # REVISED: ใช้ rand_realistic_datetime
            joined_at = rand_realistic_datetime(800, 0, start_hour=6, end_hour=23)
            is_admin = 1 if random.random() < 0.05 else 0
            try:
                cur.execute("INSERT INTO communities_users(community_id, user_id, joined_at, is_admin) VALUES(?,?,?,?)",
                            (cid, u, joined_at, is_admin))
            except sqlite3.IntegrityError:
                pass

        # 7) Events and event participants
    
    # --- NEW LOGIC START: Setup Community Data and Themes ---
    
    # 1. Fetch Community Names and associated members for better event generation
    community_data = {}
    cur.execute("SELECT community_id, name FROM communities")
    # Store community names to determine event themes
    for cid, name in cur.fetchall():
        community_data[cid] = {'name': name, 'members': []}

    cur.execute("SELECT community_id, user_id FROM communities_users")
    # Store community members to prioritize participation
    for cid, uid in cur.fetchall():
        if cid in community_data:
            community_data[cid]['members'].append(uid)

    # 2. Define event themes based on community names for realistic names/descriptions
    EVENT_THEMES = {
        'Runners': {
            'names': ['5K Fun Run', 'Weekend Trail Marathon', 'Night City Sprint', 'Interval Training Session'],
            'desc': [
                'A fun run for all skill levels.',
                'Challenge yourself on the mountain trails.',
                'Fast-paced running through the downtown area.',
                'Improve your speed and endurance.'
            ]
        },
        'Cyclists': {
            'names': ['Group Century Ride', 'Scenic Hill Climb', 'Morning Commuter Challenge'],
            'desc': [
                '100km ride with the group.',
                'Test your endurance on the steepest hills.',
                'Quick morning ride to start the day.'
            ]
        },
        'Hikers': {
            'names': ['Sunrise Mountain Trek', 'Waterfall Trail Hike', 'City Park Nature Walk'],
            'desc': [
                'Early morning hike to catch the sunrise.',
                'Explore the best natural trails.',
                'A relaxing walk in the city\'s green lung.'
            ]
        },
        'Swimmers': {
            'names': ['Pool Lap Challenge', 'Open Water Training Session', 'Triathlon Prep Swim'],
            'desc': [
                'See how many laps you can complete.',
                'Practice in the local reservoir.',
                'Focused session for triathletes.'
            ]
        },
        'Default': {
            'names': ['Fitness Meetup', 'Weekly Workout Session', 'Health Seminar'],
            'desc': [
                'A general fitness gathering.',
                'Get fit together!',
                'Learn about optimizing your health.'
            ]
        }
    }
    # --- NEW LOGIC END: Setup Community Data and Themes ---

    # Determine the list of possible Location IDs
    location_ids = list(range(1, N_LOCATIONS + 1))
    
    for eid in range(1, N_EVENTS+1):
        community_id = random.randint(1, N_COMMUNITIES)
        
        # 1. Generate realistic Event Name and Description based on Community
        comm_name_prefix = 'Default'
        comm_name = community_data[community_id]['name']
        for prefix in EVENT_THEMES.keys():
            if prefix in comm_name:
                comm_name_prefix = prefix
                break
        
        theme = EVENT_THEMES[comm_name_prefix]
        name = random.choice(theme['names'])
        event_descrip = random.choice(theme['desc'])
        
        # 2. Location ID - 90% chance of having a location
        location_id = random.choice(location_ids * 9 + [None])
        
        # 3. Realistic Timing: Occur between 8 AM - 8 PM (20:00)
        # Event span: random days between 200 days ago and 0 days ago
        event_start_dt_str = rand_realistic_datetime(
            start_days_ago=200,
            end_days_ago=0,
            start_hour=8,
            end_hour=20
        )
        start_dt = datetime.fromisoformat(event_start_dt_str)
        end_dt = start_dt + timedelta(hours=random.randint(1, 6))  # Events last 1 to 6 hours

        cur.execute(
            """
            INSERT INTO events(
                event_id,
                community_id,
                location_id,
                event_name,
                event_descrip,
                start_datetime,
                end_datetime
            )
            VALUES(?,?,?,?,?,?,?)
            """,
            (eid, community_id, location_id, name, event_descrip, start_dt.isoformat(), end_dt.isoformat())
        )
        
        # 4. Participants: only community members of this event
        #    และจำนวนผู้เข้าร่วมในแต่ละ Event มีความหลากหลาย
        potential_participants = community_data[community_id]['members']

        if not potential_participants:
            # ถ้า community นี้ยังไม่มีสมาชิก ก็ไม่สร้างผู้เข้าร่วมให้ event นี้
            participants = []
        else:
            community_size = len(potential_participants)

            # เลือก "อัตราการเข้าร่วม" ของ Event นี้แบบสุ่ม
            # 30%, 50%, 70% หรือ 100% (ถ่วงน้ำหนักให้เต็มบ้าง ไม่เต็มบ้าง)
            engagement_rate = random.choice(
                [0.3, 0.5, 0.7, 1.0, 1.0]  # ใส่ 1.0 ซ้ำเพื่อให้มีโอกาสเต็มสูงขึ้นหน่อย
            )

            # คำนวณจำนวนผู้เข้าร่วมจาก rate และขนาด community
            num_participants = int(round(community_size * engagement_rate))

            # กันไม่ให้เป็น 0 และไม่เกินจำนวนสมาชิกจริง
            num_participants = max(1, min(community_size, num_participants))

            # สุ่มผู้เข้าร่วมจากสมาชิก community เท่านั้น
            participants = random.sample(potential_participants, k=num_participants)

        # 4b. Insert participants
        for u in participants:
            # Weighted random: 4x chance of participating (rsvp/checked_in) vs cancelling
            status = random.choice(['rsvp', 'checked_in'] * 4 + ['cancelled']) 
            
            # checkin_datetime ต้องเกิดขึ้นหลัง start_dt
            if status == 'checked_in':
                # สุ่มเวลา Check-in หลัง start_dt แต่ต้องไม่เกิน 1 ชั่วโมงหลังเริ่ม (สมมติว่ามาเร็ว)
                checkin_dt = fake.date_time_between(
                    start_date=start_dt,
                    end_date=min(end_dt, start_dt + timedelta(hours=1))
                )
                checkin = checkin_dt.isoformat()
            else:
                checkin = None
            
            try:
                # location_id ใน event_participants คือสถานที่ Check-in (ควรเป็น location_id ของ Event)
                participant_loc_id = location_id if location_id else random.choice(location_ids)
                
                cur.execute(
                    """
                    INSERT INTO event_participants(
                        event_id,
                        user_id,
                        location_id,
                        status,
                        checkin_datetime
                    )
                    VALUES(?,?,?,?,?)
                    """,
                    (eid, u, participant_loc_id, status, checkin)
                )
            except sqlite3.IntegrityError:
                # กันกรณี user ถูก insert ซ้ำใน event เดียวกัน (หากมี unique constraint)
                pass  # กรณีที่ user ถูกสุ่มมาซ้ำ


    # 8) Goals (ตรรกะเวลา Created_at -> Start_dt -> End_dt)
    # Map ID to Activity Name (อ้างอิงจาก activity_types ล่าสุด)
    activity_type_names = [
        'Run', 'Walk', 'Cycling', 'Hike', 'Swim', 'Rowing', 
        'Strength Training', 'Yoga / Pilates', 'Hiit / Functional', 'Dance / Aerobics'
    ]
    
    for gid in range(1, N_GOALS+1):
        user_id = random.choice(user_ids)
        
        # 1. activity_type_id เป็น NOT NULL เสมอ (สุ่ม ID ระหว่าง 1-10)
        activity_type_id = random.randint(1, len(activity_type_names))
        activity_name = activity_type_names[activity_type_id - 1]
        
        # 2. กำหนด target_metric และ target_amount ให้สอดคล้องกับกิจกรรม
        target_amount = 0.0
        goal_name_template = ""
        
        # ID 1-6: กิจกรรมเน้นระยะทาง (สามารถเป็น distance_km หรือ calories)
        if activity_type_id <= 6:
            target_metric = random.choices(['distance_km', 'calories'], weights=[6, 4], k=1)[0]
            
            if target_metric == 'distance_km':
                if activity_type_id in [1, 2, 4]: 
                    target_amount = round(random.uniform(10, 150), 1) 
                elif activity_type_id == 3: 
                    target_amount = round(random.uniform(50, 500), 1) 
                else: 
                    target_amount = round(random.uniform(1, 50), 1) 
                
                goal_name_template = f"Target {target_amount} km {activity_name}"
            
            else: # target_metric == 'calories'
                target_amount = round(random.uniform(500, 10000), 0)
                goal_name_template = f"Burn {int(target_amount)} kcal with {activity_name}"
        
        # ID 7-10: กิจกรรมเน้นเวลา/ความแข็งแรง (ต้องเป็น calories)
        else:
            target_metric = 'calories'
            
            if activity_type_id == 9: 
                 target_amount = round(random.uniform(3000, 12000), 0)
                 goal_name_template = f"Master {int(target_amount)} kcal of {activity_name}"
            else: 
                 target_amount = round(random.uniform(1000, 8000), 0)
                 goal_name_template = f"Burn {int(target_amount)} kcal of {activity_name}"
        
        goal_name = goal_name_template
        
        # 4. ปรับปรุงลำดับเวลา (Created_at -> Start_dt -> End_dt)
        status = random.choices(['active', 'completed', 'failed'], weights=[6, 3, 1], k=1)[0]
        
        # REVISED: 4a. กำหนด created_at (datetime object) ด้วยเวลาที่สมจริง (6 AM - 11 PM)
        created_at_dt_str = rand_realistic_datetime(400, 0, start_hour=6, end_hour=23)
        created_at_dt = datetime.fromisoformat(created_at_dt_str)
        
        # 4b. กำหนด start_dt (date object)
        # เป้าหมายเริ่มในวันเดียวกับที่สร้าง หรือ 1-15 วันหลังจากสร้าง
        start_date_range_end = created_at_dt + timedelta(days=15)
        # ต้องไม่ให้ start_dt อยู่ในอนาคตไกลเกินไป (ไม่เกิน 7 วันนับจากวันนี้)
        start_dt = fake.date_time_between(start_date=created_at_dt, 
                                          end_date=min(start_date_range_end, datetime.utcnow() + timedelta(days=7))).date()
        
        # 4c. กำหนด end_dt (date object) ตาม Status
        
        if status == 'completed':
             # ต้องสิ้นสุดในอดีต (1-60 วันหลังเริ่ม)
             end_dt = start_dt + timedelta(days=random.randint(1, 60)) 
        elif status == 'failed':
             # ต้องสิ้นสุดในอดีต (1-90 วันหลังเริ่ม)
             end_dt = start_dt + timedelta(days=random.randint(1, 90)) 
        else: # active
             # ต้องสิ้นสุดในอนาคต (1-90 วันจากวันนี้)
             end_dt = (datetime.utcnow() + timedelta(days=random.randint(1, 90))).date()

        # created_at ใช้ isoformat
        created_at = created_at_dt.isoformat()
        
        cur.execute("""INSERT INTO goals(goal_id, user_id, activity_type_id, goal_name, target_amount, target_metric, start_dt, end_dt, status, created_at)
                       VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (gid, user_id, activity_type_id, goal_name, target_amount, target_metric, start_dt.isoformat(), end_dt.isoformat(), status, created_at))


    # 9) Biometrics
    biometric_id = 1
    today = datetime.utcnow().date() 

    for user_id in user_ids:
        # 1. กำหนดส่วนสูง (Height) และน้ำหนักพื้นฐาน (Base Weight) เพียงครั้งเดียวต่อผู้ใช้
        # ส่วนสูง: ควรคงที่ตลอดช่วงเวลา
        user_height = round(random.uniform(150, 195), 1) # ส่วนสูง (cm)
        # น้ำหนักพื้นฐาน: ใช้เป็นจุดเริ่มต้นสำหรับการผันผวน
        base_weight = round(random.uniform(55, 90), 1) 

        # วนลูปตามจำนวนวันย้อนหลังที่ต้องการ
        for day_offset in range(DAYS_HISTORY):
            # 2. คำนวณวันที่และเวลาที่วัด
            measured_date = today - timedelta(days=day_offset)
            # measured_at_dt: ช่วงเวลาที่เหมาะสม (6 AM ถึง 10 PM)
            measured_at_dt = measured_date + timedelta(hours=random.randint(6, 22), minutes=random.randint(0, 59))
            measured_at = measured_at_dt.isoformat()

            # 3. สร้างข้อมูล Biometric
            # น้ำหนัก: ผันผวนเล็กน้อยจาก Base Weight เพื่อความสมจริง ( +/- 1.5 kg)
            weight_fluctuation = random.uniform(-1.5, 1.5) 
            weight = round(max(40.0, base_weight + weight_fluctuation), 1)
            
            height = user_height # ใช้ค่าที่กำหนดไว้ในลูปผู้ใช้ (คงที่)
            
            bp = f"{random.randint(100,130)}/{random.randint(60,85)}"
            hr = random.randint(50, 100)
            sleep_score = random.randint(40, 100)
            
            # 4. INSERT
            cur.execute("""INSERT INTO biometrics(biometric_id, user_id, weight, weight_unit, height, height_unit, blood_pressure_avg, heart_rate_avg, sleep_score, measured_at)
                           VALUES(?,?,?,?,?,?,?,?,?,?)""",
                        (biometric_id, user_id, weight, 'kg', height, 'cm', bp, hr, sleep_score, measured_at))
            
            biometric_id += 1

    # 10) Notifications
    n_id = 1
    for _ in range(N_NOTIFICATIONS):
        user_id = random.choice(user_ids)
        # ตรวจสอบว่า device_id มีอยู่จริงหรือไม่
        device_ref = random.choice(range(1, device_id)) if device_id > 1 and random.random() > 0.5 else None
        ntype = random.choice(['reminder','promotion','system'])
        title = fake.sentence(nb_words=4)
        body = fake.sentence(nb_words=10)
        
        # FIX: เพิ่ม start_hour=6 และ end_hour=23 (ช่วงเวลาปกติที่ระบบส่งการแจ้งเตือน)
        created_at = rand_realistic_datetime(120, 0, start_hour=6, end_hour=23)
        
        is_read = 1 if random.random()>0.6 else 0
        cur.execute("""INSERT INTO notification(notification_id, user_id, device_id, notification_type, title, body, created_at, is_read)
                       VALUES(?,?,?,?,?,?,?,?)""",
                    (n_id, user_id, device_ref, ntype, title, body, created_at, is_read))
        n_id += 1

    # 11) News
    news_id = 1
    for _ in range(N_NEWS):
        subj = f"News {news_id}: {fake.word().capitalize()}"
        des = fake.paragraph(nb_sentences=2)
        
        # FIX: เพิ่ม start_hour=8 และ end_hour=20 (เวลาทำการที่ข่าวถูกสร้าง/เผยแพร่)
        start_dt = rand_realistic_datetime(300, 0, start_hour=8, end_hour=20)
        
        end_dt = None
        created_by = random.choice(user_ids)
        cur.execute("""INSERT INTO news(news_id, news_subject, news_descrip, news_start_datetime, news_end_datetime, is_read, created_by_user_id)
                       VALUES(?,?,?,?,?,?,?)""",
                    (news_id, subj, des, start_dt, end_dt, 0, created_by))
        news_id += 1

    # 12) Achievements
    a_id = 1
    for _ in range(N_ACHIEVEMENTS):
        user_id = random.choice(user_ids)
        code = f"ACH{random.randint(1000,9999)}"
        name = random.choice(['First Run','Marathon','Century Ride','Early Riser','Consistency'])
        des = f"Awarded for {name.lower()}"
        
        # FIX: แก้ไขบรรทัดนี้ โดยเพิ่ม start_hour=6 และ end_hour=23 
        # (กำหนดเวลาได้รับรางวัลให้อยู่ในช่วงที่ผู้ใช้ใช้งานระบบ)
        earned_at = rand_realistic_datetime(400, 0, start_hour=6, end_hour=23)
        
        try:
            cur.execute("""INSERT INTO achievements(achievement_id, user_id, a_code, a_name, a_descrip, earned_at)
                           VALUES(?,?,?,?,?,?)""", (a_id, user_id, code, name, des, earned_at))
            a_id += 1
        except sqlite3.IntegrityError:
            pass # skip duplicate codes

    # 13) Missions
    for mid in range(1, N_MISSIONS+1):
        mission_difficulty_id = random.randint(1, len(mission_diff))
        activity_type_id = random.randint(1, len(activity_types))
        name = f"Mission {mid} - {random.choice(['Sprint','Endurance','Weekend'])}"
        des = fake.sentence(nb_words=8)
        reward = random.randint(50, 1000)
        cur.execute("""INSERT INTO missions(mission_id, mission_difficulty_id, activity_type_id, name, description, reward_points)
                       VALUES(?,?,?,?,?,?)""",
                    (mid, mission_difficulty_id, activity_type_id, name, des, reward))

    # <<< 14) User Missions (Mission Completion Logs) (เพิ่มใหม่) >>>
    print("Populating mission_completion...")
    # ใช้เซ็ตเพื่อติดตามคู่ (user_id, mission_id) ที่ทำสำเร็จแล้ว ป้องกันการซ้ำซ้อน
    completed_missions = set() 

    # คำนวณจำนวนภารกิจที่ทำสำเร็จสูงสุดที่เป็นไปได้ (N_USERS * N_MISSIONS)
    MAX_POSSIBLE_COMPLETIONS = N_USERS * N_MISSIONS
    # กำหนดจำนวนเป้าหมายที่แท้จริง
    TARGET_COMPLETIONS = min(N_USER_MISSIONS, MAX_POSSIBLE_COMPLETIONS)
    
    i = 0
    # วนลูปจนกว่าจะถึงจำนวนภารกิจที่ทำสำเร็จตามเป้าหมาย (หรือจนกว่าจะครบทุกคู่ที่เป็นไปได้)
    while i < TARGET_COMPLETIONS:
        user_id = random.choice(user_ids)
        mission_id = random.randint(1, N_MISSIONS)
        
        # ตรวจสอบว่าภารกิจนี้เคยทำสำเร็จไปแล้วหรือไม่ (เนื่องจากเราใช้ Composite Primary Key)
        if (user_id, mission_id) in completed_missions:
            continue
            
        # ใช้ช่วงเวลาที่สมจริง (ผู้ใช้มักจะทำภารกิจสำเร็จในช่วงเวลาใช้งาน)
        completed_at = rand_realistic_datetime(800, 0, start_hour=6, end_hour=23)
        
        try:
            cur.execute("INSERT INTO mission_completion(user_id, mission_id, completed_at, is_rewarded) VALUES(?,?,?,?)",
                        (user_id, mission_id, completed_at, 1))
            completed_missions.add((user_id, mission_id))
            i += 1 # นับเฉพาะรายการที่ใส่ได้จริง
        except sqlite3.IntegrityError:
            # ไม่ควรเกิดขึ้นเพราะเราตรวจสอบด้วย set แล้ว
            continue 

    conn.commit()
    conn.close()
    print("Mock data population completed.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error:", e)
        raise