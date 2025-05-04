from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from futurefocus_backend.get_staff_hours_this_week import fetch_staff_hours_this_week_all
from futurefocus_backend.centre_funding_bot import fetch_occupancy_data
from futurefocus_backend.companies import company_config  # ✅ added this line

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "FutureFocusAgent is up and running 🚀"}

@app.get("/staff-hours-this-week/all")
def get_all_staff_hours():
    try:
        return fetch_staff_hours_this_week_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/occupancy")
def get_occupancy_from_ui():
    try:
        return fetch_occupancy_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

