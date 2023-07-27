from typing import Optional
from app.exceptions import BookingAppException
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.auth.auth import authenticate_user, create_access_token, get_current_user
from app.repositories.users import UsersRepository

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form["username"], form["password"]
        user = await UsersRepository().find_one_or_none(email=email)
        existing_user = authenticate_user(user, password)
        if existing_user.role == "admin":
            access_token = create_access_token({"sub": str(existing_user.id)})
            request.session.update({"booking_access_token": access_token})
            return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        token = request.session.get("booking_access_token")
        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        try:
            await get_current_user(token)
        except BookingAppException:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)


authentication_backend = AdminAuth(secret_key="...")
