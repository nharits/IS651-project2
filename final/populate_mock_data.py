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
DB_PATH = "garmin_clone.db"
# เพิ่มในส่วน Configuration ด้านบน (พร้อมกับ N_USERS, N_ACTIVITIES, ฯลฯ)
DAYS_HISTORY = 30        # For biometrics: collect one record per user per day for this many days (Keep)

# List of tables to clear to ensure the script is idempotent (can be re-run)
TABLES_TO_CLEAR = [
    'genders', 'mission_difficulties', 'activity_types', 'locations', 'users',
    'devices', 'activities', 'communities', 'communities_users', 'events',
    'event_participants', 'goals', 'biometrics', 'notification', 'news',
    'achievements', 'missions'
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

    mission_diff = ['easy','medium','hard']
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
    # Data for Thai Provinces (Province Name, Latitude, Longitude) for realistic location generation
# (Complete list of 77 provinces)
    THAI_LOCATIONS = [
    ("Bangkok", 13.7563, 100.5018), 
    ("Amnat Charoen", 15.8647, 104.6293), 
    ("Ang Thong", 14.5888, 100.3804), 
    ("Bueng Kan", 18.3687, 103.6508), 
    ("Buri Ram", 15.0062, 103.1091), 
    ("Chachoengsao", 13.6888, 101.0716), 
    ("Chai Nat", 15.1963, 100.1257), 
    ("Chaiyaphum", 15.8166, 102.0493), 
    ("Chanthaburi", 12.6074, 102.1158), 
    ("Chiang Mai", 18.7061, 98.9950), 
    ("Chiang Rai", 19.9079, 99.8325), 
    ("Chonburi", 13.3602, 100.9840), 
    ("Chumphon", 10.4623, 99.1557), 
    ("Kalasin", 16.4485, 103.5262), 
    ("Kamphaeng Phet", 16.4674, 99.5255), 
    ("Kanchanaburi", 14.0076, 99.5165), 
    ("Khon Kaen", 16.4444, 102.8354), 
    ("Krabi", 8.0833, 98.9213), 
    ("Lampang", 18.2936, 99.5085), 
    ("Lamphun", 18.5861, 99.0061), 
    ("Loei", 17.4725, 101.8398), 
    ("Lopburi", 14.7997, 100.6720), 
    ("Mae Hong Son", 19.3021, 97.9686), 
    ("Maha Sarakham", 16.1950, 103.2423), 
    ("Mukdahan", 16.5451, 104.6857), 
    ("Nakhon Nayok", 14.2057, 101.2183), 
    ("Nakhon Pathom", 13.8239, 100.0784), 
    ("Nakhon Phanom", 17.4086, 104.7831), 
    ("Nakhon Ratchasima", 14.9783, 102.0992), 
    ("Nakhon Sawan", 15.6946, 100.1197), 
    ("Nakhon Si Thammarat", 8.4208, 99.9692), 
    ("Nan", 18.7779, 100.7712), 
    ("Narathiwat", 6.4279, 101.8267), 
    ("Nong Bua Lamphu", 17.2036, 102.4042), 
    ("Nong Khai", 17.8761, 102.7562), 
    ("Nonthaburi", 13.8856, 100.4682), 
    ("Pathum Thani", 14.0205, 100.5244), 
    ("Pattani", 6.8661, 101.2290), 
    ("Phang Nga", 8.4485, 98.5297), 
    ("Phatthalung", 7.6186, 100.0763), 
    ("Phetchabun", 16.4257, 101.0772), 
    ("Phetchaburi", 13.1118, 99.9329), 
    ("Phichit", 16.2699, 100.3541), 
    ("Phitsanulok", 16.8251, 100.2646), 
    ("Phrae", 18.1469, 100.1472), 
    ("Phra Nakhon Si Ayutthaya", 14.3508, 100.5684), 
    ("Phuket", 7.8804, 98.3923), 
    ("Prachinburi", 14.0494, 101.3854), 
    ("Prachuap Khiri Khan", 11.8159, 99.7997), 
    ("Ranong", 9.9602, 98.6366), 
    ("Ratchaburi", 13.5358, 99.8174), 
    ("Rayong", 12.6766, 101.2778), 
    ("Roi Et", 16.0506, 103.6542), 
    ("Sa Kaeo", 13.8441, 102.5020), 
    ("Sakon Nakhon", 17.1558, 104.1481), 
    ("Samut Prakan", 13.5997, 100.5985), 
    ("Samut Sakhon", 13.5583, 100.2783), 
    ("Samut Songkhram", 14.0531, 99.9536), 
    ("Saraburi", 14.5165, 100.9168), 
    ("Satun", 6.6111, 99.9829), 
    ("Singburi", 14.8872, 100.3957), 
    ("Sisaket", 15.1189, 104.1481), 
    ("Songkhla", 7.1896, 100.5986), 
    ("Sukhothai", 17.0094, 99.7842), 
    ("Suphan Buri", 14.4754, 100.0818), 
    ("Surat Thani", 9.1418, 99.3299), 
    ("Surin", 14.8824, 103.4984), 
    ("Tak", 16.8770, 99.1232), 
    ("Trang", 7.5501, 99.6105), 
    ("Trat", 12.2392, 102.5061), 
    ("Ubon Ratchathani", 15.2285, 104.8576), 
    ("Udon Thani", 17.3942, 102.7845), 
    ("Uthai Thani", 15.3789, 100.0381), 
    ("Uttaradit", 17.6256, 100.0886), 
    ("Yala", 6.5510, 101.2721), 
    ("Yasothon", 15.8118, 104.1542),
    ("Phayao", 19.1918, 99.8973) 
    ]
    # NEW LOGIC: Use all 77 provinces of THAI_LOCATIONS exactly once.
    loc_id = 1
    # วนลูปตามรายการจังหวัดโดยตรง
    for province_data in THAI_LOCATIONS:
        
        city = province_data[0] # ชื่อจังหวัด (เช่น "Bangkok")
        base_lat = province_data[1] 
        base_lon = province_data[2]
        
        # 1. เพิ่มค่า Jitter (การสั่น) เล็กน้อยเพื่อจำลองตำแหน่งเฉพาะในจังหวัดนั้น
        # Jitter +/- 0.1 องศา ประมาณ +/- 11 กิโลเมตร
        lat = round(base_lat + random.uniform(-0.1, 0.1), 6) 
        lon = round(base_lon + random.uniform(-0.1, 0.1), 6)
        
        # 2. INSERT
        cur.execute("INSERT INTO locations(location_id,city,location_latitude,location_longitude) VALUES(?,?,?,?)",
                    (loc_id, city, lat, lon))
        
        loc_id += 1 # เพิ่ม Location ID
        
        # ถ้า N_LOCATIONS ถูกตั้งไว้น้อยกว่า 77 หรือต้องการหยุดที่จำนวนที่กำหนด
        if loc_id > N_LOCATIONS:
            break

    # 3) Users
    user_ids = []
    for uid in range(1, N_USERS+1):
        gender_id = random.randint(1, len(genders))
        first = fake.first_name()
        last = fake.last_name()
        username = (first + last + str(random.randint(1,999))).lower()
        email = username + "@example.com"
        phone = fake.msisdn()[:12]
        
        # FIX: เพิ่ม start_hour=6 และ end_hour=23 เพื่อกำหนดช่วงเวลาลงทะเบียนให้สมจริง
        registration_date = rand_realistic_datetime(800, 0, start_hour=6, end_hour=23)  # registered within last ~2 years
        
        bday = fake.date_of_birth(minimum_age=18, maximum_age=70).isoformat()
        is_active = 1 if random.random() > 0.05 else 0
        user_verify = 1 if random.random() > 0.2 else 0
        cur.execute("""INSERT INTO users(user_id, gender_id, first_name, last_name, username, email, phone_number, user_verify, registration_date, user_birthday, is_active)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                    (uid, gender_id, first, last, username, email, phone, user_verify, registration_date, bday, is_active))
        user_ids.append(uid)

    # 4) Devices (some users have devices)
    device_models = ['Garmin Forerunner 945','Garmin Vivoactive 4','GenericPhone','Garmin Fenix 6','Other']
    device_id = 1
    for _ in range(N_DEVICES):
        user_id = random.choice(user_ids)
        model = random.choice(device_models)
        # REVISED: ใช้ rand_realistic_datetime
        created_at = rand_realistic_datetime(800, 0, start_hour=6, end_hour=23)
        cur.execute("INSERT INTO devices(device_id, user_id, device_model, created_at) VALUES(?,?,?,?)",
                    (device_id, user_id, model, created_at))
        device_id += 1

   # 5) Activities (ตรรกะเวลาสอดคล้องกับกิจกรรม ถูกกำหนดไว้เฉพาะแล้ว)
    activity_id = 1
    
    # ใช้นโยบายการกำหนดค่าขอบเขตสูงสุดที่ปลอดภัยที่สุด
    # max_device_id คือ ID อุปกรณ์ที่มีอยู่จริงสูงสุด (N_DEVICES)
    max_device_id_to_link = max(1, device_id - 1) 
    
    for _ in range(N_ACTIVITIES):
        user_id = random.choice(user_ids)
        activity_type_id = random.randint(1, len(activity_types)) # สุ่มจากประเภทกิจกรรม 1-10
        loc_id = random.randint(1, N_LOCATIONS)
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
        
        # 2a. กำหนดวันที่ในอดีต (ไม่เกิน 720 วัน)
        date_of_activity = datetime.utcnow().date() - timedelta(days=random.randint(0, 720))
        
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
            'desc': ['A fun run for all skill levels.', 'Challenge yourself on the mountain trails.', 'Fast-paced running through the downtown area.', 'Improve your speed and endurance.']
        },
        'Cyclists': {
            'names': ['Group Century Ride', 'Scenic Hill Climb', 'Morning Commuter Challenge'],
            'desc': ['100km ride with the group.', 'Test your endurance on the steepest hills.', 'Quick morning ride to start the day.']
        },
        'Hikers': {
            'names': ['Sunrise Mountain Trek', 'Waterfall Trail Hike', 'City Park Nature Walk'],
            'desc': ['Early morning hike to catch the sunrise.', 'Explore the best natural trails.', 'A relaxing walk in the city\'s green lung.']
        },
        'Swimmers': {
            'names': ['Pool Lap Challenge', 'Open Water Training Session', 'Triathlon Prep Swim'],
            'desc': ['See how many laps you can complete.', 'Practice in the local reservoir.', 'Focused session for triathletes.']
        },
        'Default': {
            'names': ['Fitness Meetup', 'Weekly Workout Session', 'Health Seminar'],
            'desc': ['A general fitness gathering.', 'Get fit together!', 'Learn about optimizing your health.']
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
        # Event span: random days between 200 days ago and 100 days from now
        event_start_dt_str = rand_realistic_datetime(start_days_ago=200, end_days_ago=-100, start_hour=8, end_hour=20)
        start_dt = datetime.fromisoformat(event_start_dt_str)
        end_dt = start_dt + timedelta(hours=random.randint(1, 6)) # Events last 1 to 6 hours

        cur.execute("INSERT INTO events(event_id, community_id, location_id, event_name, event_descrip, start_datetime, end_datetime) VALUES(?,?,?,?,?,?,?)",
                    (eid, community_id, location_id, name, event_descrip, start_dt.isoformat(), end_dt.isoformat()))
        
        # 4. Participants: Prioritize Community Members and increase volume
        
        # Set number of participants to be between 10 and 150 (for BI)
        MAX_PARTICIPANTS = min(len(user_ids), 150)
        num_participants = random.randint(10, MAX_PARTICIPANTS) 
        
        # 4a. Get users from the hosting community (prioritize)
        potential_participants = community_data[community_id]['members']
        
        # Sample participants, prioritizing community members
        if len(potential_participants) >= num_participants:
             # Sample directly from community members (high engagement)
             participants = random.sample(potential_participants, k=num_participants)
        else:
             # Take all community members, and supplement with random users
             participants = list(potential_participants)
             supplemental_users = random.sample([u for u in user_ids if u not in participants], 
                                                k=num_participants - len(participants))
             participants.extend(supplemental_users)

        # 4b. Insert participants
        for u in participants:
            # Weighted random: 4x chance of participating (rsvp/checked_in) vs cancelling
            status = random.choice(['rsvp','checked_in'] * 4 + ['cancelled']) 
            
            # checkin_datetime ต้องเกิดขึ้นหลัง start_dt
            if status == 'checked_in':
                # สุ่มเวลา Check-in หลัง start_dt แต่ต้องไม่เกิน 1 ชั่วโมงหลังเริ่ม (สมมติว่ามาเร็ว)
                checkin_dt = fake.date_time_between(start_date=start_dt, end_date=min(end_dt, start_dt + timedelta(hours=1)))
                checkin = checkin_dt.isoformat()
            else:
                checkin = None
            
            try:
                # location_id ใน event_participants คือสถานที่ Check-in (ควรเป็น location_id ของ Event)
                participant_loc_id = location_id if location_id else random.choice(location_ids)
                
                cur.execute("INSERT INTO event_participants(event_id, user_id, location_id, status, checkin_datetime) VALUES(?,?,?,?,?)",
                            (eid, u, participant_loc_id, status, checkin))
            except sqlite3.IntegrityError:
                pass # กรณีที่ user ถูกสุ่มมาซ้ำ    

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

    conn.commit()
    conn.close()
    print("Mock data population completed.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error:", e)
        raise