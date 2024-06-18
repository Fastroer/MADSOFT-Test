from fastapi import FastAPI
from routes.memes import router

public_app = FastAPI(docs_url="/api")

public_app.include_router(router)
