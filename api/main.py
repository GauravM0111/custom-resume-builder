from fastapi import FastAPI
from fastapi.params import Depends
from fastapi.responses import RedirectResponse
from models.users import User
from routers.oauth.google import router as google_oauth_router
from services.session_service import login_required, UserDependency

app = FastAPI()
app.include_router(google_oauth_router)


@app.get("/")
@login_required
async def read_root(user: UserDependency):
    return dict(user)

@app.get("/signin")
async def sign_in():
    return RedirectResponse(google_oauth_router.url_path_for("/"))
