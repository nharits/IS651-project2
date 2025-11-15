import pandas as pd
import numpy as np
from io import BytesIO
import zipfile
from datetime import datetime, timedelta

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
# 3. SOURCE DEVICES
# ----------------------------
source_devices = devices.copy()
source_devices.rename(columns={'device_id':'source_device_id','device_name':'source_device_name'}, inplace=True)

# ----------------------------
# 4. ACTIVITY TYPES
# ----------------------------
activity_types = pd.DataFrame({
    'activity_type_id': [1,2,3,4,5],
    'activity_name': ['Running','Walking','Cycling','Strength','Swimming']
})

# ----------------------------
# 5. LOCATIONS
# ----------------------------
locations = pd.DataFrame({
    'location_id': [1,2,3],
    'location_name': ['Park','Trail','Gym']
})

# ----------------------------
# 6. ACTIVITIES (~2400 rows)
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
            source_device_id = np.random.choice([1,2,3])
            duration_sec = np.random.randint(1800, 5400)
            distance_km = 0
            if activity_type_id == 1: distance_km = round(np.random.uniform(5,10),1)
            if activity_type_id == 2: distance_km = round(np.random.uniform(2,4),1)
            if activity_type_id == 3: distance_km = round(np.random.uniform(12,25),1)
            if activity_type_id == 5: distance_km = round(np.random.uniform(0.5,1.5),1)
            calories_kcal = np.random.randint(150, 700)
            start_time = datetime.combine(date.date(), datetime.min.time()) + timedelta(hours=np.random.randint(5,19), minutes=np.random.randint(0,60))
            end_time = start_time + timedelta(seconds=duration_sec)
            activity_list.append([activity_id_counter, user_id, activity_type_id, location_id, source_device_id,
                                  start_time.strftime('%Y-%m-%d %H:%M'),
                                  end_time.strftime('%Y-%m-%d %H:%M'),
                                  duration_sec, distance_km, calories_kcal,
                                  'completed',
                                  start_time.strftime('%Y-%m-%d'),
                                  start_time.strftime('%Y-%m-%d')])
            activity_id_counter += 1

activities = pd.DataFrame(activity_list, columns=['activity_id','user_id','activity_type_id','location_id','source_device_id',
                                                  'start_time','end_time','duration_sec','distance_km','calories_kcal',
                                                  'status','created_at','updated_at'])

# ----------------------------
# 7. GOALS
# ----------------------------
goals = pd.DataFrame({
    'goal_id': range(1, 51),
    'user_id': range(1, 51),
    'goal_type': np.random.choice(['Distance','Calories','Duration'], 50),
    'target_value': np.random.randint(100, 1000, 50),
    'progress': np.random.randint(0, 100, 50),
    'status': np.random.choice(['active','completed'], 50),
    'created_at': '2024-10-01',
    'updated_at': '2024-12-31'
})

# ----------------------------
# 8. MISSIONS
# ----------------------------
missions = pd.DataFrame({
    'mission_id': range(1, 21),
    'mission_name': [f'Mission {i}' for i in range(1, 21)],
    'description': [f'Description of Mission {i}' for i in range(1,21)],
    'start_date': '2024-10-01',
    'end_date': '2024-12-31'
})

# ----------------------------
# 9. ACHIEVEMENTS
# ----------------------------
achievements = pd.DataFrame({
    'achievement_id': range(1, 21),
    'user_id': np.random.choice(range(1,51),20),
    'achievement_name': [f'Achievement {i}' for i in range(1,21)],
    'description': [f'Description {i}' for i in range(1,21)],
    'achieved_at': pd.date_range(start='2024-10-01', periods=20)
})

# ----------------------------
# 10. COMMUNITIES
# ----------------------------
communities = pd.DataFrame({
    'community_id': range(1,6),
    'community_name': ['Runners Club','Cyclists Club','Swimmers Club','Gym Friends','Walking Group'],
    'description': ['A community for activity enthusiasts']*5
})

# ----------------------------
# 11. EVENTS
# ----------------------------
events = pd.DataFrame({
    'event_id': range(1,11),
    'event_name': [f'Event {i}' for i in range(1,11)],
    'community_id': np.random.choice(range(1,6),10),
    'start_date': pd.date_range('2024-10-05', periods=10),
    'end_date': pd.date_range('2024-10-05', periods=10) + pd.Timedelta(days=1)
})

# ----------------------------
# 12. NOTIFICATIONS
# ----------------------------
notifications = pd.DataFrame({
    'notification_id': range(1,11),
    'user_id': np.random.choice(range(1,51),10),
    'message': [f'Notification {i}' for i in range(1,11)],
    'read_status': np.random.choice(['read','unread'],10),
    'created_at': pd.date_range('2024-10-01', periods=10)
})

# ----------------------------
# 13. NEWS
# ----------------------------
news = pd.DataFrame({
    'news_id': range(1,11),
    'title': [f'News Title {i}' for i in range(1,11)],
    'content': [f'Content of news {i}' for i in range(1,11)],
    'published_at': pd.date_range('2024-10-01', periods=10)
})

# ----------------------------
# 14. CREATE ZIP WITH ALL CSVs
# ----------------------------
csv_files = {
    'users.csv': users,
    'devices.csv': devices,
    'source_devices.csv': source_devices,
    'activity_types.csv': activity_types,
    'locations.csv': locations,
    'activities.csv': activities,
    'goals.csv': goals,
    'missions.csv': missions,
    'achievements.csv': achievements,
    'communities.csv': communities,
    'events.csv': events,
    'notifications.csv': notifications,
    'news.csv': news
}

with zipfile.ZipFile('garmin_complete_dataset.zip', 'w', zipfile.ZIP_DEFLATED) as zip_file:
    for name, df in csv_files.items():
        csv_bytes = df.to_csv(index=False).encode('utf-8')
        zip_file.writestr(name, csv_bytes)

print("ZIP file 'garmin_complete_dataset.zip' created successfully with all tables!")
