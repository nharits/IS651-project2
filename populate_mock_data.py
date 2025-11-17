# populate_mock_data.py
import sqlite3
from faker import Faker
import random
from datetime import datetime, timedelta

DB_PATH = "garmin_like.db"
fake = Faker()

NUM_USERS = 300
NUM_ACTIVITIES_PER_USER = (3, 15)  # range per user
NUM_COMMUNITIES = 12

def get_conn():
    return sqlite3.connect(DB_PATH)

def seed_lookups(conn):
    cur = conn.cursor()
    genders = [('male',), ('female',), ('other',)]
    cur.executemany("INSERT INTO genders (name) VALUES (?)", genders)

    activity_types = [('running',), ('cycling',), ('walking',), ('swimming',)]
    cur.executemany("INSERT INTO activity_types (type_name) VALUES (?)", activity_types)

    locations = [('Bangkok',), ('Chiang Mai',), ('Phuket',), ('Unknown',)]
    cur.executemany("INSERT INTO locations (location_province) VALUES (?)", locations)

    difficulties = [('easy',), ('medium',), ('hard',)]
    cur.executemany("INSERT INTO mission_difficulties (name) VALUES (?)", difficulties)

    conn.commit()

def seed_users(conn):
    cur = conn.cursor()
    users = []
    for _ in range(NUM_USERS):
        name = fake.first_name() + " " + fake.last_name()
        email = fake.unique.email()
        phone = fake.phone_number()
        gender_id = random.choice([1,2,3])
        reg_date = fake.date_time_between(start_date='-1y', end_date='now').isoformat()
        users.append((gender_id, name, phone, email, 'active', reg_date, None, 'user'))
    cur.executemany("""
        INSERT INTO users (gender_id, user_name, user_phone, user_email, user_status, registration_date, user_birthday, user_role, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, users)
    conn.commit()

def seed_devices(conn):
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    users = [r[0] for r in cur.fetchall()]
    devices = []
    for u in users:
        # each user may have 0-2 devices
        for _ in range(random.choices([0,1,2], [0.2,0.6,0.2])[0]):
            model = random.choice(['Watch A', 'Watch B', 'Phone X', 'Tracker Z'])
            devices.append((u, model))
    cur.executemany("INSERT INTO devices (user_id, device_model, created_at) VALUES (?, ?, datetime('now'))", devices)
    conn.commit()

def seed_activities(conn):
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    user_ids = [r[0] for r in cur.fetchall()]
    activities = []
    for uid in user_ids:
        count = random.randint(*NUM_ACTIVITIES_PER_USER)
        for i in range(count):
            act_type = random.randint(1,4)
            # random start in last 180 days
            start = datetime.utcnow() - timedelta(days=random.randint(0,180), hours=random.randint(0,23), minutes=random.randint(0,59))
            duration = random.randint(10*60, 120*60)  # 10 min - 2 hrs
            end = start + timedelta(seconds=duration)
            distance = round(random.uniform(1.0, 30.0) if act_type in (1,2) else random.uniform(0.5, 2.0), 2)
            calories = round(distance * random.uniform(50,100) / 1.0, 1)
            device_id = None
            # 60% chance device exists
            if random.random() < 0.6:
                cur.execute("SELECT device_id FROM devices WHERE user_id = ? ORDER BY RANDOM() LIMIT 1", (uid,))
                r = cur.fetchone()
                if r: device_id = r[0]
            loc = random.randint(1,4)
            activities.append((uid, act_type, loc, device_id, start.isoformat(), end.isoformat(), duration, distance, calories))
    cur.executemany("""
        INSERT INTO activities (user_id, activity_type_id, location_id, device_id, start_time, end_time, duration_sec, distance_km, calories_kcal, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, activities)
    conn.commit()

def seed_biometrics(conn):
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    user_ids = [r[0] for r in cur.fetchall()]
    rows = []
    for uid in user_ids:
        # generate 3-12 biometric records per user across last 6 months
        for _ in range(random.randint(3, 12)):
            days_ago = random.randint(0, 180)
            recorded = datetime.utcnow() - timedelta(days=days_ago)
            weight = round(random.uniform(50, 95), 1)
            height = random.randint(150, 190)
            hr = random.randint(55, 95)
            sleep = random.randint(40, 95)
            rows.append((uid, recorded.isoformat(), weight, height, None, None, None, hr, sleep))
    cur.executemany("""
        INSERT INTO biometrics (user_id, recorded_at, weight_kg, height_cm, blood_type, bp_systolic, bp_diastolic, heart_rate_avg, sleep_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()

def seed_goals(conn):
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    user_ids = [r[0] for r in cur.fetchall()]
    goals = []
    for uid in random.sample(user_ids, int(len(user_ids) * 0.4)):  # 40% set a goal
        atype = random.randint(1,4)
        # target between 10 and 200 km depending on type
        target = round(random.uniform(10, 200), 1) if atype in (1,2) else round(random.uniform(5000, 20000), 0)
        unit = 'km' if atype in (1,2) else 'steps'
        start = (datetime.utcnow() - timedelta(days=random.randint(0,60))).isoformat()
        end = (datetime.utcnow() + timedelta(days=random.randint(7,60))).isoformat()
        name = f"{unit} goal {target}"
        goals.append((uid, atype, name, target, unit, start, end))
    cur.executemany("""
        INSERT INTO goals (user_id, activity_type_id, goal_name, target_value, target_unit, start_at, end_at, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'active', datetime('now'))
    """, goals)
    conn.commit()

def seed_communities(conn):
    cur = conn.cursor()
    comms = [(f"Community {i}", fake.sentence(nb_words=4)) for i in range(1, NUM_COMMUNITIES+1)]
    cur.executemany("INSERT INTO communities (community_name, description, created_at) VALUES (?, ?, datetime('now'))", comms)
    conn.commit()

def seed_community_members(conn):
    cur = conn.cursor()
    cur.execute("SELECT community_id FROM communities")
    communities = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT user_id FROM users")
    users = [r[0] for r in cur.fetchall()]
    rows = []
    for c in communities:
        members = random.sample(users, k=max(5, int(len(users)*0.05)))  # each community 5% of users
        for u in members:
            role = random.choice(['member','moderator','member','member'])
            joined = (datetime.utcnow() - timedelta(days=random.randint(0,365))).isoformat()
            rows.append((c,u,joined,role))
    cur.executemany("INSERT INTO communities_users (community_id, user_id, joined_at, role) VALUES (?, ?, ?, ?)", rows)
    conn.commit()

def main():
    conn = get_conn()
    seed_lookups(conn)
    seed_users(conn)
    seed_devices(conn)
    seed_activities(conn)
    seed_biometrics(conn)
    seed_goals(conn)
    seed_communities(conn)
    seed_community_members(conn)
    conn.close()
    print("Mock data populated.")

if __name__ == "__main__":
    main()
