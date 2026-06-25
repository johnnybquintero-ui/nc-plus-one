from fastapi import FastAPI

from src.events import router as events_router
from src.auth import router as auth_router

app = FastAPI(title="NC Plus One Events API", debug=True)

app.include_router(events_router)
app.include_router(auth_router)