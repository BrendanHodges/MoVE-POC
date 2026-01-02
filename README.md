# FastAPI App

## Setup

1. Make sure Python is installed

2. Install dependencies:
   
Run this in Terminal:  

- **pip install -r requirements.txt**
- For me pip install doesn't work so I have to do "python -m pip install -r requirements.txt" but it might just work for you I don't know

3. Within the static folder add a data folder and put us_states and counties jsons.


## Run the Server

Start the FastAPI server in terminal with:
uvicorn main:app --reload
- Might have to do "python -m" before again

## Access the App

Open your browser and go to:
http://127.0.0.1:8000

## Stop the Server

Press CTRL + C in the terminal.
