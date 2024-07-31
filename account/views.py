import urllib.parse
from datetime import datetime

from passlib.hash import pbkdf2_sha1
from robyn import Response, SubRouter, Request, logger
from sqlalchemy import or_

from account.models import User
from account.token import decode_reset_password, create_access_token, set_cookie, verify_decode, redirect_to_profile, \
    auth_required, get_email_visited, get_user_visited
from common.execute import get_from, filter_model
from common.utils import is_valid_email, is_strong_password, redirect_response
from config.db import async_session
from config.settings import settings, templates

# Constants
key = settings.SECRET_KEY
algorithm = settings.JWT_ALGORITHM
EMAIL_TOKEN_EXPIRY_MINUTES = settings.EMAIL_TOKEN_EXPIRY_MINUTES

# Define the auth router
auth = SubRouter(__name__, prefix="/auth")


# Route handlers
@auth.get("/register")
@redirect_to_profile()
async def get_register(request: Request):
    context = {"request": request}
    return templates.render_template("/auth/register.html", **context)


@auth.post("/register")
@redirect_to_profile()
async def user_register(request: Request):
    async with async_session() as session:
        try:
            obj = dict(urllib.parse.parse_qsl(request.body))
            user_name = obj.get("name")
            user_email = obj.get("email")
            user_password = obj.get("password")
            if not is_valid_email(user_email):
                return Response(
                    status_code=400,
                    headers={"Content-Type": "text/plain"},
                    description="Invalid email format."
                )

            user_exist = await filter_model(session, User, (or_(User.name == user_name, User.email == user_email)))
            if user_exist:
                return Response(
                    status_code=400,
                    headers={"Content-Type": "text/plain"},
                    description="Name or email already registered."
                )

            user_data = {
                "name": user_name,
                "email": user_email,
                "password": pbkdf2_sha1.hash(user_password)
            }
            user = User(**user_data)
            session.add(user)
            await session.commit()

            payload = {"email": user.email, "scope": "email_verification"}
            verify_mail_token = create_access_token(payload)
            vrf = f"{request.url.scheme}://{request.url.host}/auth/email-verify?token={verify_mail_token}"

            context = {"request": request, "token": vrf}
            return templates.render_template("/auth/t_verif.html", **context)
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to register user: {e}")
            return Response(
                status_code=500,
                headers={"Content-Type": "text/plain"},
                description="Internal server error."
            )


@auth.get("/login")
@redirect_to_profile()
async def get_login(request: Request):
    context = {"request": request}
    return templates.render_template("/auth/login.html", **context)


@auth.post("/login")
@redirect_to_profile()
async def post_login(request: Request):
    async with async_session() as session:
        try:
            obj = dict(urllib.parse.parse_qsl(request.body))
            email = obj.get("email")
            password = obj.get("password")

            if not (is_valid_email(email) and password):
                return Response(
                    status_code=400,
                    headers={"Content-Type": "text/plain"},
                    description="Missing or invalid email or password."
                )

            user = await get_from(session, User, User.email, email)
            if not user:
                return Response(
                    status_code=404,
                    headers={"Content-Type": "text/plain"},
                    description="User not found."
                )

            if not user.email_verified:
                return Response(
                    status_code=401,
                    headers={"Content-Type": "text/plain"},
                    description="Email not verified."
                )

            if not pbkdf2_sha1.verify(password, user.password):
                return Response(
                    status_code=400,
                    headers={"Content-Type": "text/plain"},
                    description="Invalid password."
                )

            user.last_login_date = datetime.now()
            session.add(user)
            await session.commit()

            payload = {"email": user.email, "scope": "email_verification"}
            token = create_access_token(payload)

            return Response(
                status_code=302,
                headers={"Set-Cookie": set_cookie(token), "Location": "/"},
                description="Redirecting to home."
            )
        except Exception as e:
            logger.error(f"An error occurred during login: {e}")
            return Response(
                status_code=500,
                headers={"Content-Type": "text/plain"},
                description="Internal server error."
            )


@auth.get("/logout")
@auth_required()
async def get_user_logout(request: Request):
    try:
        email = await get_email_visited(request)
        async with async_session() as session:
            user = await get_from(session, User, User.email, email)
            if user and user.email == email:
                auth_ = True
                context = {"request": request, "auth": auth_, "user": user}
                return templates.render_template("/auth/logout.html", **context)
        return Response(
            status_code=403,
            headers={"Content-Type": "text/plain"},
            description="Unauthorized access."
        )
    except Exception as e:
        logger.error(f"An error occurred during logout: {e}")
        return Response(
            status_code=500,
            headers={"Content-Type": "text/plain"},
            description="Internal server error."
        )


@auth.post("/logout")
@auth_required()
async def user_logout(request: Request):
    try:
        email = await get_email_visited(request)
        if not is_valid_email(email):
            return Response(
                status_code=400,
                headers={"Content-Type": "text/plain"},
                description="Invalid email in token payload."
            )

        async with async_session() as session:
            user = await get_from(session, User, User.email, email)
            if not user or user.email != email:
                return Response(
                    status_code=400,
                    headers={"Content-Type": "text/plain"},
                    description="Invalid user."
                )

        return Response(
            status_code=302,
            headers={"Set-Cookie": set_cookie('', 0), "Location": "/"},
            description="Logout successful, redirecting..."
        )
    except Exception as e:
        logger.error(f"An error occurred during logout: {e}")
        return Response(
            status_code=500,
            headers={"Content-Type": "text/plain"},
            description="Internal server error."
        )


@auth.get("/email-verify")
@redirect_to_profile()
async def verify_email(request: Request):
    try:
        async with async_session() as session:
            email = await verify_decode(request)
            if not is_valid_email(email):
                return redirect_response("/auth/email-verify-resend")

            user = await get_from(session, User, User.email, email)
            if not user or user.email != email:
                return redirect_response("/auth/email-verify-resend")

            user.email_verified = True
            user.is_active = True
            await session.commit()

            return redirect_response("/auth/login")
    except Exception as e:
        logger.error(f"An error occurred during email verification: {e}")
        return Response(
            status_code=500,
            headers={"Content-Type": "text/plain"},
            description="Internal server error."
        )


@auth.get("/email-verify-resend")
@redirect_to_profile()
async def get_resend_email(request: Request):
    context = {"request": request}
    return templates.render_template("/auth/resend.html", **context)


@auth.post("/email-verify-resend")
async def resend_email(request: Request):
    async with async_session() as session:
        try:
            obj = dict(urllib.parse.parse_qsl(request.body))
            email = obj.get("email")

            if not is_valid_email(email):
                return redirect_response("/auth/email-verify-resend")

            user = await get_from(session, User, User.email, email)
            if not user:
                return Response(
                    status_code=404,
                    headers={"Content-Type": "text/plain"},
                    description="User not found."
                )

            if user.email_verified:
                return redirect_response("/auth/login")

            payload = {"email": user.email, "scope": "email_verification"}
            verify_mail_token = create_access_token(payload)
            vrf = f"{request.url.scheme}://{request.url.host}/auth/email-verify?token={verify_mail_token}"

            context = {"request": request, "token": vrf}
            return templates.render_template("/auth/t_verif.html", **context)
        except Exception as e:
            logger.error(f"An error occurred during email resend: {e}")
            return Response(
                status_code=500,
                headers={"Content-Type": "text/plain"},
                description="Internal server error."
            )


@auth.get("/reset-password")
@redirect_to_profile()
async def get_reset_password(request: Request):
    context = {"request": request}
    return templates.render_template("/auth/reset-password.html", **context)


@auth.post("/reset-password")
async def reset_password(request: Request):
    async with async_session() as session:
        try:
            obj = dict(urllib.parse.parse_qsl(request.body))
            email = obj.get("email")

            if not is_valid_email(email):
                return Response(
                    status_code=400,
                    headers={"Content-Type": "text/plain"},
                    description="Invalid email format."
                )

            user = await get_from(session, User, User.email, email)
            if not user:
                return Response(
                    status_code=404,
                    headers={"Content-Type": "text/plain"},
                    description="User not found."
                )

            payload = {"email": user.email, "scope": "reset_password"}
            reset_password_token = create_access_token(payload)
            vrf = f"{request.url.scheme}://{request.url.host}/auth/reset-password-confirm?token={reset_password_token}"

            context = {"request": request, "token": vrf}
            return templates.render_template("/auth/t_pwd_verif.html", **context)
        except Exception as e:
            logger.error(f"An error occurred during reset password: {e}")
            return Response(
                status_code=500,
                headers={"Content-Type": "text/plain"},
                description="Internal server error."
            )


@auth.get("/reset-password-confirm")
@redirect_to_profile()
async def get_reset_password_confirm(request: Request):
    try:
        email = await decode_reset_password(request)
        if not is_valid_email(email):
            return redirect_response("/auth/reset-password")

        context = {"request": request}
        return templates.render_template("auth/reset-password-confirm.html", **context)
    except Exception as e:
        logger.error(f"An error occurred during password confirmation: {e}")
        return Response(
            status_code=500,
            headers={"Content-Type": "text/plain"},
            description="Internal server error."
        )


@auth.post("/reset-password-confirm")
async def reset_password_confirm(request: Request):
    try:
        email = await decode_reset_password(request)
        if not is_valid_email(email):
            return redirect_response("/auth/reset-password")

        obj = dict(urllib.parse.parse_qsl(request.body))
        new_password = obj.get("password")
        if is_strong_password(new_password):
            async with async_session() as session:
                user = await get_from(session, User, User.email, email)
                user.password = pbkdf2_sha1.hash(new_password)
                session.add(user)
                await session.commit()
            return redirect_response("/auth/login")
        return Response(
            status_code=302,
            headers={"Content-Type": "text/plain"},
            description=f"A strong password should meet the following criteria: {new_password}"
        )
    except Exception as e:
        logger.error(f"An error occurred during password reset: {e}")
        return Response(
            status_code=500,
            headers={"Content-Type": "text/plain"},
            description="Internal server error."
        )


@auth.get("/detail")
@auth_required()
async def get_user_detail(request: Request):
    try:
        async with async_session() as session:
            user = await get_user_visited(request, session)
            if user:
                auth_ = True
                context = {"request": request, "auth": auth_, "user": user}
                return templates.render_template("/auth/details.html", **context)
        return Response(
            status_code=403,
            headers={"Content-Type": "text/plain"},
            description="Unauthorized access."
        )
    except Exception as e:
        logger.error(f"An error occurred during user detail retrieval: {e}")
        return Response(
            status_code=500,
            headers={"Content-Type": "text/plain"},
            description="Internal server error."
        )
