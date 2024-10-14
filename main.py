from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from routers.oauth.google import router as google_oauth_router
from routers.users import router as users_router
from routers.resume import router as resume_router
from auth.auth import user_authentication_middleware
from settings.settings import TEMPLATES, UNAUTHENTICATED_ENDPOINTS
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.include_router(google_oauth_router)
app.include_router(users_router)
app.include_router(resume_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.middleware("http")
async def user_authentication_middleware_router(request: Request, call_next):
    if request.url.path in UNAUTHENTICATED_ENDPOINTS:
        return await call_next(request)
    
    return await user_authentication_middleware(request, call_next)


@app.get("/")
async def read_root(request: Request):
    return TEMPLATES.TemplateResponse("home.html", {"request": request, "user": request.state.user})


@app.get("/signin")
async def sign_in(guest_id: str):
    return RedirectResponse(google_oauth_router.url_path_for("sign_in", guest_id=guest_id))
