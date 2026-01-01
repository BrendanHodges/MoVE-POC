from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.queries import fetch_move_equation_scores
from fastapi import Query, HTTPException

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

# WHEN Fetch request is made it leads directly to this function (Check queries to see how data is pulled)
@app.get('/api/county-scores')
def county_MoVE_score():
    data = fetch_move_equation_scores()
    return data
