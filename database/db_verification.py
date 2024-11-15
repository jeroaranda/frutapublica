# verify_migration.py
from database.db import get_session
from models.models import Flora, Observation, User
import pandas as pd

def verify_migration():
    session = get_session()
    
    try:
        # Read original CSV
        df = pd.read_csv('flora.csv')
        
        # Get counts from database
        users_count = session.query(User).count()
        floras_count = session.query(Flora).count()
        observations_count = session.query(Observation).count()
        
        print("\n=== Migration Verification ===")
        print(f"Original CSV rows: {len(df)}")
        print(f"Database observations: {observations_count}")
        print(f"Unique users in database: {users_count}")
        print(f"Unique flora types in database: {floras_count}")
        
        # Verify some random observations
        print("\nSample Observations:")
        observations = session.query(Observation).join(Flora).join(User).limit(5).all()
        for obs in observations:
            print(f"\nFlora: {obs.flora.name}")
            print(f"User: {obs.user.username}")
            print(f"Location: ({obs.lat}, {obs.lon})")
            print(f"Description: {obs.description}")
        
    finally:
        session.close()

if __name__ == "__main__":
    verify_migration()