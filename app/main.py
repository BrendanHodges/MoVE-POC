from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.queries import fetch_move_equation_scores, fetch_county_census_data
from fastapi import Query, HTTPException
import pandas as pd

app = FastAPI()

# Mount static directory, Starts everything
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates directory
templates = Jinja2Templates(directory="templates")


@app.get("/health")
def health_check():
    return {"status": "ok"}

# INITIALIZES THE APP, OPENS index.html
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get('/api/state-scores')
def state_MoVE_score():
    countyScores = fetch_move_equation_scores()
    stateScores = countyScores.groupby('state_id').agg(
        {
            'move_score_0_100': 'mean',
            'county_id': 'count'
        }
    ).reset_index()

    stateScoresDict = {
        str(row['state_id']): {
            "score": round(row['move_score_0_100'], 2),
        }
        for _, row in stateScores.iterrows()
    }

    return stateScoresDict

@app.get('/api/county-scores')
def county_MoVE_score():
    data = fetch_move_equation_scores()
    print(f"Raw Data: {data}")
    countyScores = {
        str(row['county_id']): {
            "name": row['county_name'],
            "score": round(row['move_score_0_100'], 2)
        }
        for _, row in data.iterrows()
        }
    print(f"County Scores: {countyScores}")
    return countyScores

# @app.get('/api/county-census{county_id}')
# def county_census_data(county_id: str = Query(..., description="The GEOID of the county")):
#     data = fetch_county_census_data(county_id)
    
#     county_data = data[data['county_id'] == int(county_id)]

#     if county_data.empty:
#         raise HTTPException(status_code=404, detail="County not found")


#     return census_data