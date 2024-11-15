# frutapublica/database/db_init.py
from models.models import Base, Flora, Observation, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

def get_engine():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")
    return create_engine(database_url)

def init_database():
    engine = get_engine()
    
    # Create database if it doesn't exist
    if not database_exists(engine.url):
        create_database(engine.url)
        print(f"Created database")
    
    # Create all tables
    Base.metadata.create_all(engine)
    print("Created all database tables successfully")

def migrate_flora_data():
    """Migrate existing flora.csv data to the new database"""
    # Get the path to the data file
    current_dir = Path(__file__).parent.parent  # Go up to frutapublica folder
    csv_path = current_dir / 'data' / 'flora.csv'
    
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Create dictionaries to store user and flora mappings
        users = {}
        floras = {}
        
        # Process each row in the CSV
        for _, row in df.iterrows():
            # Get or create user
            username = row['usuario']
            if username not in users:
                user = session.query(User).filter_by(username=username).first()
                if not user:
                    user = User(username=username)
                    session.add(user)
                    session.flush()
                users[username] = user
            
            # Get or create flora
            flora_name = row['flora inferida']
            if flora_name not in floras:
                flora = session.query(Flora).filter_by(name=flora_name).first()
                if not flora:
                    flora = Flora(name=flora_name)
                    session.add(flora)
                    session.flush()
                floras[flora_name] = flora
            
            # Create observation
            observation = Observation(
                flora_id=floras[flora_name].id,
                user_id=users[username].id,
                datetime=pd.to_datetime(row['datetime']),
                lat=row['lat'],
                lon=row['lon'],
                address=row['dirección'],
                description=row['observaciones']
            )
            session.add(observation)
        
        # Commit all changes
        session.commit()
        print(f"Successfully migrated {len(df)} observations")
        print(f"Created {len(users)} users")
        print(f"Created {len(floras)} flora types")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        session.rollback()
        raise
    finally:
        session.close()

def main():
    print("Starting database initialization and data migration...")
    init_database()
    migrate_flora_data()
    print("Database initialization and data migration completed!")

if __name__ == "__main__":
    main()