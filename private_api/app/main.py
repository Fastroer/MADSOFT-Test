from fastapi import FastAPI
from app.routes import media

app = FastAPI(docs_url="/private-api")

app.include_router(media.router)
