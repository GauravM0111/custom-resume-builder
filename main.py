from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from auth.auth import user_authentication_middleware
from routers.index import router as index_router
from routers.oauth.google import router as google_oauth_router
from routers.resume import router as resume_router
from routers.users import router as users_router
from settings.settings import UNAUTHENTICATED_ENDPOINTS

app = FastAPI()
app.include_router(index_router)
app.include_router(google_oauth_router)
app.include_router(users_router)
app.include_router(resume_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.middleware("http")
async def user_authentication_middleware_router(request: Request, call_next):
    if request.url.path in UNAUTHENTICATED_ENDPOINTS:
        return await call_next(request)

    return await user_authentication_middleware(request, call_next)
