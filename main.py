from fastapi import FastAPI
# from routers.admin import router as admin_router
from routers.users import users_router
from routers.categories import router as categories_router
from routers.messages import messages_router
from routers.replies import router as replies_router
from routers.topics import topics_router
# from routers.votes import router as votes_router
import uvicorn


app = FastAPI()
# app.include_router(admin_router)
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(messages_router)
app.include_router(replies_router)
app.include_router(topics_router)
# app.include_router(votes_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)