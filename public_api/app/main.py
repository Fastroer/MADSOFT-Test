from fastapi import FastAPI
from app.routes import memes

app = FastAPI(docs_url="/api")

app.include_router(memes.router)
