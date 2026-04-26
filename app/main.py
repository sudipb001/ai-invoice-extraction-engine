from fastapi import FastAPI

from app.api.upload import router as upload_router
from app.api.extract import router as extract_router
from app.api.parse import router as parse_router
from app.api.export import router as export_router
from app.api.history import router as history_router

app = FastAPI(title="AI Invoice Extraction Engine")

@app.get("/")
def home():
    return {"message": "API Running Successfully"}

app.include_router(upload_router)
app.include_router(extract_router)
app.include_router(parse_router)
app.include_router(export_router)
app.include_router(history_router)
