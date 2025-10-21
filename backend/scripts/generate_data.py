import json
import random
from datetime import datetime, timedelta
from faker import Faker

# Configuration 
NUM_CLUBS = 5
NUM_MEMBERS = 100
CHECKIN_DAYS = 90 # Generate check-ins for the last 120 days.
DATA_DIR = "../data/" # Save files in the 'data' directory.

# Initialize Faker to generate realistic data
fake = Faker()

# 1. Generate Clubs 
print("Generating cluns...")
clubs = []
for i in range(1, NUM_CLUBS + 1):
    clubs.append({
        "club_id": i,
        "club_name": f"{fake.city()} Fitness Center",
        "city": fake.city()
    })

with open(f"{DATA_DIR}clubs.json", "w") as f:
    json.dump(clubs, f, indent=4)
print(f" Generated {len(clubs)} clubs.")


# 2. Generate Members 
print("\nGenerating members...")
members = []
for i in range(1, NUM_MEMBERS + 1):
    start_date = fake.date_between(start_date="-5y", end_date="today")
    members.append({
        "member_id": i,
        "club_id": random.choice(clubs)["club_id"], # Assign to a random club
        "name": fake.name(),
        "birthday": fake.date_of_birth(minimum_age=16, maximum_age=80).isoformat(),
        "start_date": start_date.isoformat(),
        "active_status": random.choices([True, False], weights=[0.8, 0.2])[0] # 80% active
    })

with open(f"{DATA_DIR}members.json", "w") as f:
    json.dump(members, f, indent=4)
print(f" Generated {len(members)} members.")


# 3. Generate Check-ins 
print("\nGenerating check-ins...")
checkins = []
checkin_id_counter = 1
today = datetime.now()
date_range_start = today - timedelta(days=CHECKIN_DAYS)

# Only active members can check in
active_members = [m for m in members if m["active_status"]]

for member in active_members:
    # Each active member checks in a random number of times
    num_checkins = random.randint(0, 20)
    for _ in range(num_checkins):
        checkin_timestamp = fake.date_time_between(start_date=date_range_start, end_date=today)
        checkins.append({
            "checkin_id": checkin_id_counter,
            "member_id": member["member_id"],
            "club_id": member["club_id"], # Assume member checks into their home club
            "timestamp": checkin_timestamp.isoformat()
        })
        checkin_id_counter += 1

with open(f"{DATA_DIR}checkins.json", "w") as f:
    json.dump(checkins, f, indent=4)
print(f" Generated {len(checkins)} check-ins for the last {CHECKIN_DAYS} days.")

print("\n🎉 Mock data generation complete!")