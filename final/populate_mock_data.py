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
N_LOCATIONS = 100         # locations
N_ACTIVITIES = 3000      # activity records
N_COMMUNITIES = 20
N_EVENTS = 80
N_GOALS = 300
N_BIOMETRICS = 600
N_DEVICES = 350
N_NOTIFICATIONS = 1200
N_NEWS = 30
N_ACHIEVEMENTS = 600
N_MISSIONS = 25
DB_PATH = "garmin_clone.db"
# เพิ่มในส่วน Configuration ด้านบน (พร้อมกับ N_USERS, N_ACTIVITIES, ฯลฯ)
DAYS_HISTORY = 30        # For biometrics: collect one record per user per day for this many days

# <<< ต้องเพิ่มส่วนนี้ที่นี่ >>>
# List of tables to clear to ensure the script is idempotent (can be re-run)
TABLES_TO_CLEAR = [
    'genders', 'mission_difficulties', 'activity_types', 'locations', 'users',
    'devices', 'activities', 'communities', 'communities_users', 'events',
    'event_participants', 'goals', 'biometrics', 'notification', 'news',
    'achievements', 'missions'
]
# <<< จบส่วนที่ต้องเพิ่ม >>>

fake = Faker()
Faker.seed(1)
random.seed(1)

def iso_days_ago(days):
    return (datetime.utcnow() - timedelta(days=days)).isoformat()

def rand_between_dates(start_days_ago, end_days_ago):
    start = datetime.utcnow() - timedelta(days=start_days_ago)
    end = datetime.utcnow() - timedelta(days=end_days_ago)
    return fake.date_time_between(start_date=start, end_date=end).isoformat()

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Ensure foreign_keys on
    cur.execute("PRAGMA foreign_keys = ON;")

    # 0) NEW: Clear data from all tables to allow re-running the script
    print("Clearing existing mock data...")
    
    # <<< แก้ไขตรงนี้: ใช้ .reverse() หรือ reversed() เพื่อลบในลำดับย้อนกลับ >>>
    # เราจะใช้ reversed() เพื่อลบตารางลูกก่อนตารางแม่
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

    activity_types = ['run','walk','ride','hike','swim','strength']
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
    # NEW LOGIC: Use realistic Thai province coordinates with small jitter
    for loc_id in range(1, N_LOCATIONS+1):
        # 1. สุ่มเลือกข้อมูลจังหวัดจาก THAI_LOCATIONS
        province_data = random.choice(THAI_LOCATIONS)
        city = province_data[0] # <<--- ชื่อภาษาอังกฤษจะถูกดึงมาที่นี่
        base_lat = province_data[1] 
        base_lon = province_data[2]
        
        # 2. เพิ่มค่า Jitter (การสั่น) เล็กน้อยเพื่อจำลองตำแหน่งเฉพาะในจังหวัดนั้น
        lat = round(base_lat + random.uniform(-0.1, 0.1), 6) 
        lon = round(base_lon + random.uniform(-0.1, 0.1), 6)
        
        cur.execute("INSERT INTO locations(location_id,city,location_latitude,location_longitude) VALUES(?,?,?,?)",
                    (loc_id, city, lat, lon))

    # 3) Users
    user_ids = []
    for uid in range(1, N_USERS+1):
        gender_id = random.randint(1, len(genders))
        first = fake.first_name()
        last = fake.last_name()
        username = (first + last + str(random.randint(1,999))).lower()
        email = username + "@example.com"
        phone = fake.msisdn()[:12]
        registration_date = rand_between_dates(800, 0)  # registered within last ~2 years
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
        created_at = rand_between_dates(800, 0)
        cur.execute("INSERT INTO devices(device_id, user_id, device_model, created_at) VALUES(?,?,?,?)",
                    (device_id, user_id, model, created_at))
        device_id += 1

   # 5) Activities
    activity_id = 1
    
    # ใช้นโยบายการกำหนดค่าขอบเขตสูงสุดที่ปลอดภัยที่สุด
    # max_device_id คือ ID อุปกรณ์ที่มีอยู่จริงสูงสุด (N_DEVICES)
    # เราใช้ max(1, device_id - 1) เพื่อรับประกันว่าขอบเขตบนอย่างน้อยคือ 1 
    # แม้ในกรณีที่ N_DEVICES ถูกตั้งเป็น 0
    max_device_id_to_link = max(1, device_id - 1) 
    
    for _ in range(N_ACTIVITIES):
        user_id = random.choice(user_ids)
        activity_type_id = random.randint(1, len(activity_types))
        loc_id = random.randint(1, N_LOCATIONS)
        
        # NEW: กำหนด device_id เสมอ (ไม่มี NULL)
        # สุ่ม ID ระหว่าง 1 ถึง max_device_id_to_link
        device_ref = random.randint(1, max_device_id_to_link)

        # realistic durations: 10 - 180 minutes
        duration_min = random.randint(10, 180)
        end_dt = datetime.utcnow() - timedelta(days=random.randint(0, 720), minutes=random.randint(0, 1440))
        start_dt = end_dt - timedelta(minutes=duration_min)
        
        # distance: สุ่มโดยอิงจากประเภทกิจกรรม
        if activity_type_id == 1:
             avg_dist = 5
        elif activity_type_id == 2:
             avg_dist = 15
        else:
             avg_dist = 2
             
        distance = round(max(0.1, random.gauss(avg_dist, 5)), 2)
        calories = int(max(50, distance * random.uniform(50, 80)))
        
        is_verified = 1 if random.random() > 0.3 else 0
        created_at = (start_dt + timedelta(minutes=1)).isoformat()
        updated_at = (start_dt + timedelta(minutes=2)).isoformat()
        
        cur.execute("""INSERT INTO activities(activity_id, user_id, activity_type_id, location_id, device_id, start_datetime, end_datetime, distance_km, calories_kcal, is_verified, created_at, updated_at)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (activity_id, user_id, activity_type_id, loc_id, device_ref, start_dt.isoformat(), end_dt.isoformat(), distance, calories, is_verified, created_at, updated_at))
        activity_id += 1

    # 6) Communities and community users
    for cid in range(1, N_COMMUNITIES+1):
        location_id = random.randint(1, N_LOCATIONS)
        name = f"{random.choice(['Runners','Cyclists','Hikers','Swimmers'])} Group {cid}"
        description = fake.sentence(nb_words=8)
        created_at = rand_between_dates(800, 0)
        cur.execute("INSERT INTO communities(community_id, location_id, name, description, is_public, created_at) VALUES(?,?,?,?,?,?)",
                    (cid, location_id, name, description, 1 if random.random()>0.1 else 0, created_at))
        # members
        members = random.sample(user_ids, k=max(3, random.randint(5, 40)))
        for u in members:
            joined_at = rand_between_dates(800, 0)
            is_admin = 1 if random.random() < 0.05 else 0
            try:
                cur.execute("INSERT INTO communities_users(community_id, user_id, joined_at, is_admin) VALUES(?,?,?,?)",
                            (cid, u, joined_at, is_admin))
            except sqlite3.IntegrityError:
                pass

    # 7) Events and event participants
    for eid in range(1, N_EVENTS+1):
        community_id = random.randint(1, N_COMMUNITIES)
        location_id = random.choice([random.randint(1, N_LOCATIONS), None])
        name = f"Event {eid} - {fake.word().capitalize()}"
        event_descrip = fake.sentence(nb_words=12)
        start_dt = datetime.utcnow() + timedelta(days=random.randint(-200, 100))
        end_dt = start_dt + timedelta(hours=random.randint(1, 6))
        cur.execute("INSERT INTO events(event_id, community_id, location_id, event_name, event_descrip, start_datetime, end_datetime) VALUES(?,?,?,?,?,?,?)",
                    (eid, community_id, location_id, name, event_descrip, start_dt.isoformat(), end_dt.isoformat()))
        # participants
        num_participants = random.randint(3, 60)
        participants = random.sample(user_ids, k=min(len(user_ids), num_participants))
        for u in participants:
            status = random.choice(['rsvp','checked_in','cancelled'])
            checkin = rand_between_dates(400, 0) if status == 'checked_in' else rand_between_dates(700, 400)
            try:
                cur.execute("INSERT INTO event_participants(event_id, user_id, location_id, status, checkin_datetime) VALUES(?,?,?,?,?)",
                            (eid, u, location_id, status, checkin))
            except sqlite3.IntegrityError:
                pass

    # 8) Goals
    for gid in range(1, N_GOALS+1):
        user_id = random.choice(user_ids)
        activity_type_id = random.choice([None, random.randint(1, len(activity_types))])
        goal_name = f"Goal {gid}"
        target_metric = random.choice(['distance_km','calories'])
        target_amount = round(random.uniform(10, 500), 2)
        start_dt = (datetime.utcnow() - timedelta(days=random.randint(0, 120))).date().isoformat()
        end_dt = (datetime.utcnow() + timedelta(days=random.randint(1, 90))).date().isoformat()
        status = random.choice(['active','completed','failed'])
        created_at = rand_between_dates(400, 0)
        cur.execute("""INSERT INTO goals(goal_id, user_id, activity_type_id, goal_name, target_amount, target_metric, start_dt, end_dt, status, created_at)
                       VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (gid, user_id, activity_type_id, goal_name, target_amount, target_metric, start_dt, end_dt, status, created_at))

    # # 9) Biometrics
    # for bid in range(1, N_BIOMETRICS+1):
    #     user_id = random.choice(user_ids)
    #     weight = round(random.uniform(50, 95), 1)
    #     height = round(random.uniform(150, 195), 1)
    #     bp = f"{random.randint(100,130)}/{random.randint(60,85)}"
    #     hr = random.randint(50, 100)
    #     sleep_score = random.randint(40, 100)
    #     for date in date_ranges:
    #         measured_at = date
    #     cur.execute("""INSERT INTO biometrics(biometric_id, user_id, weight, weight_unit, height, height_unit, blood_pressure_avg, heart_rate_avg, sleep_score, measured_at)
    #                    VALUES(?,?,?,?,?,?,?,?,?,?)""",
    #                 (bid, user_id, weight, 'kg', height, 'cm', bp, hr, sleep_score, measured_at))

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

    # ... (โค้ดส่วน 10-13 และส่วนท้ายยังคงเดิม) ...

    # 10) Notifications
    for nid in range(1, N_NOTIFICATIONS+1):
        user_id = random.choice(user_ids)
        device_ref = random.choice(range(1, device_id)) if random.random() > 0.5 else None
        ntype = random.choice(['reminder','promotion','system'])
        title = fake.sentence(nb_words=4)
        body = fake.sentence(nb_words=10)
        created_at = rand_between_dates(120, 0)
        is_read = 1 if random.random()>0.6 else 0
        cur.execute("""INSERT INTO notification(notification_id, user_id, device_id, notification_type, title, body, created_at, is_read)
                       VALUES(?,?,?,?,?,?,?,?)""",
                    (nid, user_id, device_ref, ntype, title, body, created_at, is_read))

    # 11) News
    for nid in range(1, N_NEWS+1):
        subj = f"News {nid}: {fake.word().capitalize()}"
        des = fake.paragraph(nb_sentences=2)
        start_dt = rand_between_dates(300, 0)
        end_dt = None
        created_by = random.choice(user_ids)
        cur.execute("""INSERT INTO news(news_id, news_subject, news_descrip, news_start_datetime, news_end_datetime, is_read, created_by_user_id)
                       VALUES(?,?,?,?,?,?,?)""",
                    (nid, subj, des, start_dt, end_dt, 0, created_by))

    # 12) Achievements
    a_id = 1
    for _ in range(N_ACHIEVEMENTS):
        user_id = random.choice(user_ids)
        code = f"ACH{random.randint(1000,9999)}"
        name = random.choice(['First Run','Marathon','Century Ride','Early Riser','Consistency'])
        des = f"Awarded for {name.lower()}"
        earned_at = rand_between_dates(400, 0)
        try:
            cur.execute("""INSERT INTO achievements(achievement_id, user_id, a_code, a_name, a_descrip, earned_at)
                           VALUES(?,?,?,?,?,?)""", (a_id, user_id, code, name, des, earned_at))
            a_id += 1
        except sqlite3.IntegrityError:
            # skip duplicate codes
            pass

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
