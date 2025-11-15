import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3

np.random.seed(42)

# ----------------------------
# 1. USERS
# ----------------------------
users = pd.DataFrame({
    'user_id': range(1, 51),
    'first_name': [f'User{i}' for i in range(1, 51)],
    'last_name': [f'Test{i}' for i in range(1, 51)],
    'email': [f'user{i}@example.com' for i in range(1, 51)],
    'gender': np.random.choice(['Male', 'Female'], 50),
    'birthdate': pd.date_range(start='1980-01-01', periods=50, freq='365D').strftime('%Y-%m-%d'),
    'created_at': '2024-01-01',
    'updated_at': '2024-01-01'
})

# ----------------------------
# 2. DEVICES
# ----------------------------
devices = pd.DataFrame({
    'device_id': [1, 2, 3],
    'device_name': ['Garmin Fenix 7', 'Garmin Vivosmart 5', 'Garmin Forerunner 955'],
    'device_type': ['Watch', 'Band', 'Watch']
})

# ----------------------------
# 3. ACTIVITY TYPES
# ----------------------------
activity_types = pd.DataFrame({
    'activity_type_id': [1,2,3,4,5],
    'activity_name': ['Running','Walking','Cycling','Strength','Swimming']
})

# ----------------------------
# 4. LOCATIONS
# ----------------------------
locations = pd.DataFrame({
    'location_id': [1,2,3],
    'location_name': ['Park','Trail','Gym']
})

# ----------------------------
# 5. ACTIVITIES
# ----------------------------
activity_list = []
start_date = datetime(2024, 10, 1)
end_date = datetime(2024, 12, 31)
date_range = pd.date_range(start=start_date, end=end_date)
activity_id_counter = 1

for user_id in range(1, 51):
    for date in date_range:
        for _ in range(np.random.poisson(0.6)):
            activity_type_id = np.random.choice([1,2,3,4,5])
            location_id = np.random.choice([1,2,3])
            device_id = np.random.choice([1,2,3])
            duration_sec = np.random.randint(1800, 5400)
            distance_km = 0
            if activity_type_id == 1: distance_km = round(np.random.uniform(5,10),1)
            if activity_type_id == 2: distance_km = round(np.random.uniform(2,4),1)
            if activity_type_id == 3: distance_km = round(np.random.uniform(12,25),1)
            if activity_type_id == 5: distance_km = round(np.random.uniform(0.5,1.5),1)
            calories_kcal = np.random.randint(150, 700)
            start_time = datetime.combine(date.date(), datetime.min.time()) + timedelta(hours=np.random.randint(5,19), minutes=np.random.randint(0,60))
            end_time = start_time + timedelta(seconds=duration_sec)
            activity_list.append([activity_id_counter, user_id, activity_type_id, location_id, device_id,
                                  start_time.strftime('%Y-%m-%d %H:%M'),
                                  end_time.strftime('%Y-%m-%d %H:%M'),
                                  duration_sec, distance_km, calories_kcal,
                                  'completed',
                                  start_time.strftime('%Y-%m-%d'),
                                  start_time.strftime('%Y-%m-%d')])
            activity_id_counter += 1

activities = pd.DataFrame(activity_list, columns=['activity_id','user_id','activity_type_id','location_id','device_id',
                                                  'start_time','end_time','duration_sec','distance_km','calories_kcal',
                                                  'status','created_at','updated_at'])

# ----------------------------
# 6. GOALS
# ----------------------------
goals_list = []
goal_id_counter = 1
for user_id in range(1, 51):
    goal_type = np.random.choice(['Distance','Calories','Duration'])
    target_value = np.random.randint(100, 1000)
    user_activities = activities[activities['user_id']==user_id]
    if goal_type == 'Distance':
        progress = user_activities['distance_km'].sum()
    elif goal_type == 'Calories':
        progress = user_activities['calories_kcal'].sum()
    else:
        progress = user_activities['duration_sec'].sum()//60
    status = 'completed' if progress>=target_value else 'active'
    goals_list.append([goal_id_counter, user_id, goal_type, target_value, int(progress), status, '2024-10-01','2024-12-31'])
    goal_id_counter += 1
goals = pd.DataFrame(goals_list, columns=['goal_id','user_id','goal_type','target_value','progress','status','created_at','updated_at'])

# ----------------------------
# 7. MISSIONS
# ----------------------------
missions_list = []
for i in range(1,21):
    mission_name = f'Mission {i}'
    description = f'Description of Mission {i}'
    start_date_m = datetime(2024, 10, 1)
    end_date_m = datetime(2024, 12, 31)
    activities_in_mission = np.random.choice(activities['activity_id'], size=np.random.randint(10,30), replace=False)
    missions_list.append([i, mission_name, description, start_date_m.strftime('%Y-%m-%d'), end_date_m.strftime('%Y-%m-%d'), ','.join(map(str, activities_in_mission))])
missions = pd.DataFrame(missions_list, columns=['mission_id','mission_name','description','start_date','end_date','activity_ids'])

# ----------------------------
# 8. ACHIEVEMENTS
# ----------------------------
achievements_list = []
for i in range(1,21):
    user_id = np.random.choice(range(1,51))
    activity_subset = activities[activities['user_id']==user_id].sample(n=min(3,len(activities[activities['user_id']==user_id])), random_state=42)
    achievement_name = f'Achievement {i}'
    description = f'Achievement for completing {len(activity_subset)} activities'
    achieved_at = activity_subset['end_time'].max()
    achievements_list.append([i, user_id, achievement_name, description, achieved_at])
achievements = pd.DataFrame(achievements_list, columns=['achievement_id','user_id','achievement_name','description','achieved_at'])

# ----------------------------
# 9. COMMUNITIES
# ----------------------------
communities = pd.DataFrame({
    'community_id': range(1,6),
    'community_name': ['Runners Club','Cyclists Club','Swimmers Club','Gym Friends','Walking Group'],
    'description': ['A community for activity enthusiasts']*5
})

# ----------------------------
# 10. EVENTS
# ----------------------------
events = pd.DataFrame({
    'event_id': range(1,11),
    'event_name': [f'Event {i}' for i in range(1,11)],
    'community_id': np.random.choice(communities['community_id'],10),
    'start_date': pd.date_range('2024-10-05', periods=10),
    'end_date': pd.date_range('2024-10-05', periods=10) + pd.Timedelta(days=1)
})

# ----------------------------
# 11. NOTIFICATIONS
# ----------------------------
notifications = pd.DataFrame({
    'notification_id': range(1,11),
    'user_id': np.random.choice(users['user_id'],10),
    'message': [f'Notification {i}' for i in range(1,11)],
    'read_status': np.random.choice(['read','unread'],10),
    'created_at': pd.date_range('2024-10-01', periods=10)
})

# ----------------------------
# 12. NEWS
# ----------------------------
news = pd.DataFrame({
    'news_id': range(1,11),
    'title': [f'News Title {i}' for i in range(1,11)],
    'content': [f'Content of news {i}' for i in range(1,11)],
    'published_at': pd.date_range('2024-10-01', periods=10)
})

# ----------------------------
# 13. CREATE SQLITE DATABASE WITH FOREIGN KEYS
# ----------------------------
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

# DROP TABLES IF EXIST
tables = ['activities','goals','missions','achievements','notifications','news','users','devices','activity_types','locations','communities','events']
for table in tables:
    cursor.execute(f"DROP TABLE IF EXISTS {table};")

# CREATE TABLES
cursor.execute("""
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    gender TEXT,
    birthdate TEXT,
    created_at TEXT,
    updated_at TEXT
);""")

cursor.execute("""
CREATE TABLE devices (
    device_id INTEGER PRIMARY KEY,
    device_name TEXT,
    device_type TEXT
);""")

cursor.execute("""
CREATE TABLE activity_types (
    activity_type_id INTEGER PRIMARY KEY,
    activity_name TEXT
);""")

cursor.execute("""
CREATE TABLE locations (
    location_id INTEGER PRIMARY KEY,
    location_name TEXT
);""")

cursor.execute("""
CREATE TABLE activities (
    activity_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    activity_type_id INTEGER,
    location_id INTEGER,
    device_id INTEGER,
    start_time TEXT,
    end_time TEXT,
    duration_sec INTEGER,
    distance_km REAL,
    calories_kcal INTEGER,
    status TEXT,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(activity_type_id) REFERENCES activity_types(activity_type_id),
    FOREIGN KEY(location_id) REFERENCES locations(location_id),
    FOREIGN KEY(device_id) REFERENCES devices(device_id)
);""")

cursor.execute("""
CREATE TABLE goals (
    goal_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    goal_type TEXT,
    target_value INTEGER,
    progress INTEGER,
    status TEXT,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);""")

cursor.execute("""
CREATE TABLE missions (
    mission_id INTEGER PRIMARY KEY,
    mission_name TEXT,
    description TEXT,
    start_date TEXT,
    end_date TEXT,
    activity_ids TEXT
);""")

cursor.execute("""
CREATE TABLE achievements (
    achievement_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    achievement_name TEXT,
    description TEXT,
    achieved_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);""")

cursor.execute("""
CREATE TABLE communities (
    community_id INTEGER PRIMARY KEY,
    community_name TEXT,
    description TEXT
);""")

cursor.execute("""
CREATE TABLE events (
    event_id INTEGER PRIMARY KEY,
    event_name TEXT,
    community_id INTEGER,
    start_date TEXT,
    end_date TEXT,
    FOREIGN KEY(community_id) REFERENCES communities(community_id)
);""")

cursor.execute("""
CREATE TABLE notifications (
    notification_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    message TEXT,
    read_status TEXT,
    created_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);""")

cursor.execute("""
CREATE TABLE news (
    news_id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT,
    published_at TEXT
);""")

# ----------------------------
# Insert Data
# ----------------------------
users.to_sql('users', conn, if_exists='append', index=False)
devices.to_sql('devices', conn, if_exists='append', index=False)
activity_types.to_sql('activity_types', conn, if_exists='append', index=False)
locations.to_sql('locations', conn, if_exists='append', index=False)
activities.to_sql('activities', conn, if_exists='append', index=False)
goals.to_sql('goals', conn, if_exists='append', index=False)
missions.to_sql('missions', conn, if_exists='append', index=False)
achievements.to_sql('achievements', conn, if_exists='append', index=False)
communities.to_sql('communities', conn, if_exists='append', index=False)
events.to_sql('events', conn, if_exists='append', index=False)
notifications.to_sql('notifications', conn, if_exists='append', index=False)
news.to_sql('news', conn, if_exists='append', index=False)

conn.commit()
conn.close()

print("Full SQLite database 'database.db' created successfully with all tables and foreign keys!")
