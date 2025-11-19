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
N_LOCATIONS = 50         # locations
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
    cities = ['Bangkok','Chiang Mai','Phuket','Singapore','Jakarta','Kuala Lumpur','London','New York','Sydney','Tokyo']
    for loc_id in range(1, N_LOCATIONS+1):
        city = random.choice(cities)
        lat = round(random.uniform(-37.0, 37.0), 6)
        lon = round(random.uniform(-122.0, 151.0), 6)
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
    for _ in range(N_ACTIVITIES):
        user_id = random.choice(user_ids)
        activity_type_id = random.randint(1, len(activity_types))
        loc_id = random.randint(1, N_LOCATIONS)
        # assign device sometimes
        device_ref = random.randint(1, device_id-1) if random.random() > 0.3 and device_id > 1 else None
        # realistic durations: 20 - 180 minutes
        duration_min = random.randint(10, 180)
        end_dt = datetime.utcnow() - timedelta(days=random.randint(0, 720), minutes=random.randint(0, 1440))
        start_dt = end_dt - timedelta(minutes=duration_min)
        distance = round(max(0.1, random.gauss(5 if activity_type_id == 1 else 10, 5)), 2)
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

    # 9) Biometrics
    for bid in range(1, N_BIOMETRICS+1):
        user_id = random.choice(user_ids)
        weight = round(random.uniform(50, 95), 1)
        height = round(random.uniform(150, 195), 1)
        bp = f"{random.randint(100,130)}/{random.randint(60,85)}"
        hr = random.randint(50, 100)
        sleep_score = random.randint(40, 100)
        measured_at = rand_between_dates(700, 0)
        cur.execute("""INSERT INTO biometrics(biometric_id, user_id, weight, weight_unit, height, height_unit, blood_pressure_avg, heart_rate_avg, sleep_score, measured_at)
                       VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (bid, user_id, weight, 'kg', height, 'cm', bp, hr, sleep_score, measured_at))

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
