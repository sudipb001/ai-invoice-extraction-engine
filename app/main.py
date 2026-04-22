from fastapi import FastAPI

app = FastAPI(title="AI Invoice Extraction Engine")

@app.get("/")
def home():
    return {"message": "API Running Successfully"}
