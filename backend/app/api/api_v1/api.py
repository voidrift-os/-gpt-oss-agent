from fastapi import APIRouter


from app.api.api_v1.endpoints import auth, expenses, moods, agent

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
api_router.include_router(moods.router, prefix="/moods", tags=["moods"])
api_router.include_router(agent.router, tags=["agent"])
