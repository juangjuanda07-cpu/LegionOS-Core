import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any

app = FastAPI(title="LEGION OS: ARCHIVIST KERNEL")

# --- 1. CONFIGURATION & CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. THE SMART LOADER ---
DB_FILE = "Thesis, Antithesis, Synthesis, and Abstain Archive 1-3750 Fixed.json"
ROSTER_DB = []

def load_database():
    """Loads the big JSON file with error handling."""
    global ROSTER_DB
    if not os.path.exists(DB_FILE):
        print(f"⚠️ WARNING: Could not find '{DB_FILE}'. Using empty roster.")
        return

    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
        # Handle different JSON structures (List vs Dict)
        if isinstance(raw_data, list):
            ROSTER_DB = raw_data
        elif isinstance(raw_data, dict):
            # Try to find the list inside keys like "LEGION_OS" or "ROSTER"
            for key in ["ROSTER", "LEGION_OS", "agents", "data"]:
                if key in raw_data and isinstance(raw_data[key], list):
                    ROSTER_DB = raw_data[key]
                    break
            # If still dict, maybe the root is the object wrapper
            if not ROSTER_DB and "LEGION_OS_ULTIMATE" in raw_data:
                 ROSTER_DB = raw_data["LEGION_OS_ULTIMATE"].get("ROSTER", [])
                 
        print(f"✅ SYSTEM: Successfully ingested {len(ROSTER_DB)} entities.")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR loading JSON: {e}")

# Load immediately on startup
load_database()

# --- 3. MODELS ---
class InteractionRequest(BaseModel):
    agent_a_name: str
    agent_b_name: str

# --- 4. ENDPOINTS ---
@app.get("/")
def health_check():
    return {"status": "ONLINE", "database_size": len(ROSTER_DB)}

@app.get("/roster")
def get_roster():
    # Send the raw list. Frontend handles filtering/sorting.
    return ROSTER_DB

@app.post("/analyze/crucible")
def run_crucible(req: InteractionRequest):
    # Search logic (Case insensitive)
    a = next((x for x in ROSTER_DB if x.get("name") == req.agent_a_name), None)
    b = next((x for x in ROSTER_DB if x.get("name") == req.agent_b_name), None)
    
    if not a or not b:
        raise HTTPException(status_code=404, detail="One or both agents not found.")

    # --- THE ALGORITHM ---
    score = 50
    notes = []
    
    # 1. Bloc Logic
    bloc_a = a.get("bloc", "UNKNOWN")
    bloc_b = b.get("bloc", "UNKNOWN")
    
    if bloc_a == bloc_b and bloc_a != "UNKNOWN":
        score += 40
        notes.append(f"Strategic Alignment: Both belong to {bloc_a}.")
    elif {bloc_a, bloc_b} == {"THESIS", "ANTITHESIS"}:
        score -= 40
        notes.append("Dialectical Opposition: Order vs Chaos.")
        
    # 2. IQ Resonance (If data exists)
    iq_a = a.get("triarchic_iq", {}).get("analytical", 0.5)
    iq_b = b.get("triarchic_iq", {}).get("analytical", 0.5)
    
    if abs(iq_a - iq_b) < 0.15:
        score += 10
        notes.append("Cognitive Resonance: Similar Analytical processing.")
    
    score = max(0, min(100, score))
    
    return {
        "synergy_score": score,
        "notes": notes,
        "status": "CALCULATED"
    }