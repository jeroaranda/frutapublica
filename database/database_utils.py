from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models.models import Flora, Observation, User, Recipe, RecipeIngredient
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path
import json

load_dotenv()

from database.fallback_store import FallbackStore


class _FallbackQuery:
    def __init__(self, items, attr_name):
        self._items = items
        self._attr = attr_name

    def all(self):
        # Return simple objects with attribute access
        class _Simple:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)

        return [_Simple(**{self._attr: i}) for i in self._items]


class _FallbackSession:
    """A very small session-like object used when DB is not configured.

    It only supports the minimal calls used by `Home.py`: `query(Flora).all()`
    and `query(User).all()`. It also exposes `close()` for compatibility.
    """
    def __init__(self, store: FallbackStore):
        self._store = store

    def query(self, model):
        if model is Flora:
            flora_names = sorted({r.get('flora_name') for r in self._store.all() if r.get('flora_name')})
            return _FallbackQuery(flora_names, 'name')
        if model is User:
            users = sorted({r.get('username') for r in self._store.all() if r.get('username')})
            return _FallbackQuery(users, 'username')
        # Fallback: empty
        return _FallbackQuery([], 'name')

    def close(self):
        return None


def _db_url_present():
    return bool(os.getenv('DATABASE_URL'))


def get_db_session():
    """Create and return a database session or a fallback session when no DB is configured."""
    if not _db_url_present():
        # Return a lightweight fallback session backed by CSV
        store = FallbackStore()
        return _FallbackSession(store)

    engine = create_engine(os.getenv('DATABASE_URL'))
    Session = sessionmaker(bind=engine)
    return Session()


def get_observations_df():
    """Get observations as a pandas DataFrame. Uses DB if configured, otherwise CSV fallback."""
    if not _db_url_present():
        store = FallbackStore()
        df = pd.DataFrame(store.all())
        # Ensure columns used by the front-end exist
        for c in ['id', 'datetime', 'flora_name', 'username', 'lat', 'lon', 'address', 'description']:
            if c not in df.columns:
                df[c] = None
        return df

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
    """Add a new observation to the database or append to CSV when no DB is configured."""
    if not _db_url_present():
        # Append to CSV
        csv_path = Path(__file__).parent.parent / 'data' / 'flora_data.csv'
        store = FallbackStore(csv_path)
        rows = store.all()
        max_id = max((r['id'] or 0) for r in rows) if rows else 0
        new_id = max_id + 1
        new_row = {
            'datetime': datetime.now(),
            'address': address or '',
            'lat': lat or '',
            'lon': lon or '',
            'description': description or '',
            'id': new_id,
            'flora_name': flora_name,
            'username': username,
        }
        # Append using pandas to preserve CSV structure
        df_new = pd.DataFrame([new_row])
        # Ensure we write without index and with same columns order as original file if possible
        df_new.to_csv(csv_path, mode='a', header=False, index=False)
        return new_id

    session = get_db_session()

    # Get or create flora
    flora = session.query(Flora).filter_by(name=flora_name).first()
    if not flora:
        flora = Flora(name=flora_name)
        session.add(flora)
        session.flush()

    # Get or create user
    user = session.query(User).filter_by(username=username).first()
    if not user:
        user = User(username=username)
        session.add(user)
        session.flush()

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
    """Get all recipes with their ingredients. Uses DB or a JSON fallback file."""
    if not _db_url_present():
        json_path = Path(__file__).parent.parent / 'data' / 'recipes_fallback.json'
        if not json_path.exists():
            return []
        with open(json_path, 'r', encoding='utf-8') as fh:
            return json.load(fh)

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
    """Add a new recipe with ingredients to DB or to a JSON fallback file."""
    if not _db_url_present():
        json_path = Path(__file__).parent.parent / 'data' / 'recipes_fallback.json'
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
        else:
            data = []
        new_id = max((r.get('id', 0) for r in data), default=0) + 1
        entry = {'id': new_id, 'name': name, 'prep': prep, 'ingredients': flora_names}
        data.append(entry)
        with open(json_path, 'w', encoding='utf-8') as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        return new_id

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