from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models.models import Flora, Observation, User, Recipe, RecipeIngredient
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_session():
    """Create and return a database session"""
    engine = create_engine(os.getenv('DATABASE_URL'))
    Session = sessionmaker(bind=engine)
    return Session()

def get_observations_df():
    """Get observations as a pandas DataFrame"""
    session = get_db_session()
    observations = session.query(
        Observation.id,
        Observation.datetime,
        Flora.name.label('flora_name'),
        User.username,
        Observation.lat,
        Observation.lon,
        Observation.address,
        Observation.description
    ).join(Flora).join(User).all()
    
    df = pd.DataFrame(observations)
    session.close()
    return df

def add_observation(flora_name, username, lat, lon, address, description):
    """Add a new observation to the database"""
    session = get_db_session()
    
    # Get or create flora
    flora = session.query(Flora).filter_by(name=flora_name).first()
    if not flora:
        flora = Flora(name=flora_name)
        session.add(flora)
    
    # Get or create user
    user = session.query(User).filter_by(username=username).first()
    if not user:
        user = User(username=username)
        session.add(user)
    
    # Create observation
    observation = Observation(
        flora_id=flora.id,
        user_id=user.id,
        datetime=datetime.now(),
        lat=lat,
        lon=lon,
        address=address,
        description=description
    )
    
    session.add(observation)
    session.commit()
    observation_id = observation.id
    session.close()
    return observation_id

def get_recipes():
    """Get all recipes with their ingredients"""
    session = get_db_session()
    recipes = session.query(Recipe).all()
    result = []
    for recipe in recipes:
        ingredients = [ri.flora.name for ri in recipe.ingredients]
        result.append({
            'id': recipe.id,
            'name': recipe.name,
            'prep': recipe.prep,
            'ingredients': ingredients
        })
    session.close()
    return result

def add_recipe(name, prep, flora_names):
    """Add a new recipe with ingredients"""
    session = get_db_session()
    
    # Create recipe
    recipe = Recipe(name=name, prep=prep)
    session.add(recipe)
    session.flush()  # To get the recipe ID
    
    # Add ingredients
    for flora_name in flora_names:
        flora = session.query(Flora).filter_by(name=flora_name).first()
        if not flora:
            flora = Flora(name=flora_name)
            session.add(flora)
            session.flush()
        
        recipe_ingredient = RecipeIngredient(recipe_id=recipe.id, flora_id=flora.id)
        session.add(recipe_ingredient)
    
    session.commit()
    session.close()