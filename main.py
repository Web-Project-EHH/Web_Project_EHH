import uvicorn
from fastapi import FastAPI
from routers.topics import topics_router


app = FastAPI()
app.include_router(topics_router)
