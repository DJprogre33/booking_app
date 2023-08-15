from typing import Optional

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.exceptions import BookingAppException
from app.services.auths import AuthsService
from app.utils.transaction_manager import TransactionManager
from app.dependencies import get_current_user, get_current_superuser
from app.utils.auth import get_authorization_scheme_param


transaction_manager = TransactionManager()


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> Optional[bool]:
        form = await request.form()
        email, password = form["username"], form["password"]
        token, existing_user = await AuthsService().login_user(
            transaction_manager=transaction_manager,
            password=password,
            email=email
        )
        if existing_user.role == "admin":
            request.session.update({"access_token": token.access_token})
            return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        try:
            # authenticate logic
            access_token = request.session.get("access_token")
            _, param = get_authorization_scheme_param(access_token)
            await get_current_superuser(await get_current_user(token=param))
        # if we caught BookingAppException the redirect to login page
        except BookingAppException:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)


authentication_backend = AdminAuth(secret_key="...")
