from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Flora(Base):
    __tablename__ = 'flora'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

class Observation(Base):
    __tablename__ = 'observations'
    id = Column(Integer, primary_key=True)
    flora_id = Column(Integer, ForeignKey('flora.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    datetime = Column(DateTime)
    lat = Column(Float)
    lon = Column(Float)
    address = Column(String)
    description = Column(String)
    
    flora = relationship("Flora", backref="observations")
    user = relationship("User", backref="observations")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)

class Recipe(Base):
    __tablename__ = 'recipes'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    prep = Column(String)

class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredients'
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    flora_id = Column(Integer, ForeignKey('flora.id'))

    recipe = relationship("Recipe", backref="ingredients")
    flora = relationship("Flora", backref="recipes")
