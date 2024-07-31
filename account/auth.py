from typing import Optional

from robyn import Response, Request, logger
from robyn.authentication import TokenGetter, AuthenticationHandler
from robyn.robyn import Identity

from account.token import decode_access_token, get_cookies
from common.utils import  is_valid_email


class CustomBearerGetter(TokenGetter):
    """
    Custom bearer token getter for extracting tokens from request headers.
    """

    @classmethod
    def get_token(cls, request: Request) -> Optional[str]:
        """
        Retrieve the token from the 'cookie' header if present.

        Args:
            request (Request): The incoming request object.

        Returns:
            Optional[str]: The extracted token, if available.
        """
        token = None
        if "cookie" in request.headers:
            token = get_cookies(request).get("visited")
        return token

    @classmethod
    def set_token(cls, request: Request, token: str):
        """
        Set the token in the request headers.

        Args:
            request (Request): The incoming request object.
            token (str): The token to set.
        """
        request.headers["cookie"]['visited'] = f"{token}"


class BasicAuthHandler(AuthenticationHandler):
    """
    Basic authentication handler using a custom bearer token getter.
    """

    def __init__(self, token_getter: CustomBearerGetter):
        self.token_getter = token_getter

    @property
    def unauthorized_response(self) -> Response:
        """
        Response to return when authentication fails.

        Returns:
            Response: The response object indicating unauthorized access.
        """
        return Response(
            status_code=307,
            description="Redirecting to login.",
            headers={"Location": "/auth/login"},
        )

    def authenticate(self, request: Request) -> Optional[Identity]:
        """
        Authenticate the request using the bearer token.

        Args:
            request (Request): The incoming request object.

        Returns:
            Optional[Identity]: The authenticated identity if successful, otherwise None.
        """
        token = self.token_getter.get_token(request)
        if not token:
            logger.error("No token found in the request.")
            return None
        try:
            payload = decode_access_token(token)
            payload_email = payload.get('email')
            if is_valid_email(payload_email):
                return Identity(claims={"user": payload_email})
            else:
                logger.error("No email found in token payload.")
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
        return None
