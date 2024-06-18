from fastapi import FastAPI
from private_routes.media import router

private_app = FastAPI(docs_url="/private-api")

private_app.include_router(router)
