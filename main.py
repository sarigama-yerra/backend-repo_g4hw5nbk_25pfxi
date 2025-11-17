import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Planet, Toy, Profile

app = FastAPI(title="Portls API", description="Backend for Portls immersive toy universe")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Utilities

def to_json(doc):
    if not doc:
        return doc
    if isinstance(doc, list):
        return [to_json(d) for d in doc]
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    return d


# Seed data (idempotent check)
DEFAULT_PLANETS = [
    Planet(
        name="Glubublub",
        tagline="Coral cities beneath sapphire seas",
        description="An underwater alien world with glowing reefs, bubble metros, and coral castles.",
        distance_ly=12.5,
        difficulty="Easy",
        featured_creatures=["Bubblebacks", "Coral Crabs", "Kelp Knights"],
        toy_categories=["Water Blasters", "Submarine Kits", "Sea Puzzles"],
        age_recommendation="5-10",
        travel_time="3 min through Aquaport Wormhole",
        atmosphere="High-pressure ocean, neon reefs, bubble oxygen domes",
        hero_image="/assets/planets/glubublub.jpg",
    ),
    Planet(
        name="Unicornucopia",
        tagline="Rainbow forests and shimmering skies",
        description="Lush rainbow woods, crystal rivers, and friendly unicorn guides.",
        distance_ly=8.2,
        difficulty="Easy",
        featured_creatures=["Star Unicorns", "Glimmer Owls"],
        toy_categories=["Plushies", "Craft Kits", "Rainbow Wands"],
        age_recommendation="4-9",
        travel_time="2 min through Prism Gate",
        atmosphere="Pastel mists, candy clouds, gentle breezes",
        hero_image="/assets/planets/unicornucopia.jpg",
    ),
    Planet(
        name="Lavar Major",
        tagline="Rivers of lava and magma dragons",
        description="Volcanic world with basalt fortresses and fireproof markets.",
        distance_ly=21.0,
        difficulty="Hard",
        featured_creatures=["Magma Dragons", "Lava Lizards"],
        toy_categories=["Fireproof Blocks", "Volcano Labs"],
        age_recommendation="8-12",
        travel_time="6 min through Ember Rift",
        atmosphere="Ash clouds, lava flows, heat domes",
        hero_image="/assets/planets/lavar-major.jpg",
    ),
    Planet(
        name="Whispris",
        tagline="Floating pastel cloud isles",
        description="A hush-quiet sky realm of soft isles and whisper creatures.",
        distance_ly=15.7,
        difficulty="Medium",
        featured_creatures=["Whisper Whales", "Cloud Sprites"],
        toy_categories=["Gliders", "Kite Labs", "Soft Crafts"],
        age_recommendation="6-11",
        travel_time="4 min through Nimbus Loop",
        atmosphere="Low gravity, pastel fog, sky gardens",
        hero_image="/assets/planets/whispris.jpg",
    ),
]


@app.on_event("startup")
async def seed_db():
    try:
        # Seed planets if empty
        if db is not None:
            if "planet" not in db.list_collection_names() or db["planet"].count_documents({}) == 0:
                for p in DEFAULT_PLANETS:
                    create_document("planet", p)
    except Exception:
        # If database is not configured, skip seeding gracefully
        pass


# Routes
@app.get("/")
def root():
    return {"message": "Portls API running"}


@app.get("/api/planets")
def list_planets():
    try:
        docs = get_documents("planet")
        return to_json(docs)
    except Exception:
        # Fallback to default if DB unavailable
        return [p.model_dump() for p in DEFAULT_PLANETS]


@app.get("/api/planets/{name}")
def get_planet(name: str):
    try:
        doc = db["planet"].find_one({"name": name}) if db else None
        if doc:
            return to_json(doc)
    except Exception:
        pass

    for p in DEFAULT_PLANETS:
        if p.name.lower() == name.lower():
            d = p.model_dump()
            d["id"] = name
            return d
    raise HTTPException(status_code=404, detail="Planet not found")


class TravelRequest(BaseModel):
    planet: str
    profile_name: Optional[str] = None


@app.post("/api/wormhole/initiate")
def initiate_travel(req: TravelRequest):
    # This would normally create a booking; for now just echo with a simple token
    return {
        "status": "stabilizing",
        "planet": req.planet,
        "eta": 3,
        "token": "WH-" + req.planet.replace(" ", "").upper()
    }


@app.get("/api/profile/{username}")
def get_profile(username: str):
    # Try DB
    try:
        doc = db["profile"].find_one({"username": username}) if db else None
        if doc:
            return to_json(doc)
    except Exception:
        pass
    # Default demo profile
    return {
        "username": username,
        "avatar_type": "kid",
        "badges": [{"name": "First Jump", "description": "Completed your first wormhole jump!"}],
        "achievements": [{"title": "Explorer", "description": "Visited 2 planets"}],
        "saved_planets": ["Unicornucopia", "Whispris"],
        "collectibles": ["Starlight Sticker", "Coral Coin"],
        "travel_log": ["Visited Sparklehorn Galaxy 2 days ago!"]
    }


@app.get("/api/toys")
def list_toys(planet: Optional[str] = None):
    # Example demo toys
    demo = [
        {"name": "Bubble Blaster 3000", "planet": "Glubublub", "theme": "Water", "age_range": "5-9", "price": 19.99},
        {"name": "Rainbow Wand Kit", "planet": "Unicornucopia", "theme": "Magic", "age_range": "4-8", "price": 14.99},
        {"name": "Volcano Lab Set", "planet": "Lavar Major", "theme": "Science", "age_range": "8-12", "price": 29.99},
    ]
    if planet:
        return [t for t in demo if t["planet"].lower() == planet.lower()]
    return demo


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
