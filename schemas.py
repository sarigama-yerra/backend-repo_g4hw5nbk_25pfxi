"""
Portls Database Schemas

Each Pydantic model represents a collection. Class name lowercased = collection name.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Planet(BaseModel):
    name: str = Field(..., description="Planet name")
    tagline: Optional[str] = Field(None, description="Short descriptive tagline")
    description: Optional[str] = Field(None, description="Long description of the planet")
    distance_ly: float = Field(..., ge=0, description="Distance in light-years")
    difficulty: str = Field(..., description="Adventure difficulty: Easy/Medium/Hard")
    featured_creatures: List[str] = Field(default_factory=list, description="List of notable creatures")
    toy_categories: List[str] = Field(default_factory=list, description="Toy categories found here")
    age_recommendation: str = Field(..., description="Recommended ages text (e.g., 5-10)")
    travel_time: str = Field(..., description="Estimated wormhole travel time text")
    atmosphere: Optional[str] = Field(None, description="Atmosphere & terrain summary")
    hero_image: Optional[str] = Field(None, description="Image/illustration URL")


class Toy(BaseModel):
    name: str
    planet: str = Field(..., description="Name of the source planet")
    theme: str
    age_range: str
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    image: Optional[str] = None


class Badge(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None


class Achievement(BaseModel):
    title: str
    description: Optional[str] = None
    icon: Optional[str] = None


class Profile(BaseModel):
    username: str
    avatar_type: str = Field(..., description="alien | kid | robot | creature")
    badges: List[Badge] = Field(default_factory=list)
    achievements: List[Achievement] = Field(default_factory=list)
    saved_planets: List[str] = Field(default_factory=list)
    collectibles: List[str] = Field(default_factory=list)
    travel_log: List[str] = Field(default_factory=list)
