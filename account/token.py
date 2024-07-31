import functools
from datetime import timedelta
from http.cookies import SimpleCookie
from typing import Dict, Optional

import jwt
from robyn import logger, Request

from account.models import User
from common.execute import get_from
from common.utils import now_tz, is_valid_email, redirect_response, return_response
from config.db import async_session
from config.settings import settings

# Constants
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
EMAIL_TOKEN_EXPIRY_MINUTES = settings.EMAIL_TOKEN_EXPIRY_MINUTES
COOKIE_DOMAIN = settings.COOKIE_DOMAIN


# Token Handling
async def verify_decode(request):
    """Verify and decode the email verification token from the request."""
    token = request.query_params.get("token")
    if not token:
        logger.error("No token provided.")
        return None

    try:
        decoded_token = decode_access_token(token)
        if decoded_token.get("scope") == "email_verification":
            return decoded_token.get("email")
    except jwt.ExpiredSignatureError:
        logger.error("Email token expired.")
    except jwt.InvalidTokenError:
        logger.error("Invalid email token.")
    return None


async def decode_reset_password(request):
    """Decode the reset password token from the request."""
    token = request.query_params.get("token")
    if not token:
        logger.error("No token provided.")
        return None

    try:
        decoded_token = decode_access_token(token)
        if decoded_token.get("scope") == "reset_password":
            return decoded_token.get("email")
    except jwt.ExpiredSignatureError:
        logger.error("Reset password token expired.")
    except jwt.InvalidTokenError:
        logger.error("Invalid reset password token.")
    return None


def create_access_token(data: dict, minutes: int = EMAIL_TOKEN_EXPIRY_MINUTES) -> str:
    """Create a JWT access token with the provided data and expiry time."""
    try:
        to_encode = data.copy()
        expire = now_tz() + timedelta(minutes=minutes)
        to_encode.update({"exp": expire, "iat": now_tz()})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        return "server_error_invalid_token_in_def_create_access_token"


def decode_access_token(token: str) -> dict:
    """Decode a JWT token and return the decoded data."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired.")
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        logger.error("Invalid token.")
        return {"error": "Invalid token"}


# Cookie Handling
def set_cookie(token: str, minutes: int = EMAIL_TOKEN_EXPIRY_MINUTES) -> str:
    """Set the 'visited' cookie with the provided token and expiry time."""
    try:
        expiry_time = now_tz() + timedelta(minutes=minutes)
        simple_cookie = SimpleCookie()
        simple_cookie["visited"] = token
        simple_cookie["visited"]["expires"] = expiry_time.strftime(
            "%a, %d-%b-%Y %H:%M:%S GMT"
        )
        simple_cookie["visited"]["path"] = "/"
        simple_cookie["visited"]["domain"] = COOKIE_DOMAIN
        simple_cookie["visited"]["max-age"] = str(60 * minutes)
        simple_cookie["visited"]["secure"] = True
        simple_cookie["visited"]["httponly"] = True
        simple_cookie["visited"]["samesite"] = "Lax"

        return simple_cookie.output(header="").strip()
    except Exception as e:
        logger.error(f"Error setting cookie: {e}")
        return ""


def parse_cookie(cookie_string: str) -> Dict[str, str]:
    """
    Parses a cookie string into a dictionary.

    Args:
        cookie_string (str): The raw cookie string from the request header.

    Returns:
        Dict[str, str]: A dictionary of cookie names and values.
    """
    cookie_dict: Dict[str, str] = {}
    try:
        cookie = SimpleCookie(cookie_string)
        for key, morsel in cookie.items():
            cookie_dict[key] = morsel.value
    except Exception as e:
        logger.error(f"Error parsing cookie: {e}")
    return cookie_dict


def get_cookies(request: Request) -> Optional[Dict[str, str]]:
    """
    Retrieves cookies from the request headers.

    Args:
        request (Request): The incoming request object.

    Returns:
        Optional[Dict[str, str]]: A dictionary of cookies if present, otherwise None.
    """
    try:
        cookie_header = request.headers.get("cookie")
        if cookie_header:
            return parse_cookie(cookie_header)
    except Exception as e:
        logger.error(f"Error getting cookies: {e}")
    return None


async def check_headers_valid_email(request):
    """Check if the email in the headers is valid."""
    try:
        cookie = get_cookies(request)
        token = cookie.get("visited") if cookie else None
        if token:
            payload = decode_access_token(token)
            email = payload.get("email")
            return is_valid_email(email)
    except Exception as e:
        logger.error(f"Error checking headers for valid email: {e}")
    return False


async def get_email_visited(request):
    """Retrieve the email from the 'visited' cookie."""
    try:
        cookie = get_cookies(request)
        token = cookie.get("visited") if cookie else None
        if token:
            payload = decode_access_token(token)
            email = payload.get("email")
            return email if is_valid_email(email) else None
    except Exception as e:
        logger.error(f"Error getting email from visited cookie: {e}")
    return None


async def get_user_visited(request, session):
    """Get the user associated with the visited email."""
    try:
        email = await get_email_visited(request)
        if is_valid_email(email):
            return await get_from(session, User, User.email, email)
    except Exception as e:
        logger.error(f"Error getting user from visited email: {e}")
    return None


async def get_payload_visited(request):
    """Get the payload from the 'visited' cookie."""
    try:
        cookie = get_cookies(request)
        token = cookie.get("visited") if cookie else None
        if token:
            return decode_access_token(token)
    except Exception as e:
        logger.error(f"Error getting payload from visited cookie: {e}")
    return None


def auth_required():
    """Decorator to require authentication for a route."""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            try:
                async with async_session() as session:
                    user = await get_user_visited(request, session)
                    if user:
                        return await func(request, *args, **kwargs)
                    return redirect_response("/auth/login")
            except Exception as e:
                logger.error(f"Error in auth_required decorator: {e}")
                return return_response(
                    500, {"Content-Type": "text/plain"}, "Internal server error."
                )

        return wrapper

    return decorator


def redirect_to_profile():
    """Decorator to redirect authenticated users to their profile."""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            try:
                if await check_headers_valid_email(request):
                    return redirect_response("/auth/logout", 307)
                return await func(request, *args, **kwargs)
            except Exception as e:
                logger.error(f"Error in redirect_to_profile decorator: {e}")
                return return_response(
                    500, {"Content-Type": "text/plain"}, "Internal server error."
                )

        return wrapper

    return decorator
