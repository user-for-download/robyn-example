import os

from robyn import Robyn, Request, logger

from account.auth import BasicAuthHandler, CustomBearerGetter
from account.token import create_access_token, decode_access_token, check_headers_valid_email
from account.views import auth
from common.execute import get_count_conn
# from common.startup import on_app_startup
from config.settings import BASE_DIR, templates
from leagues.view import league
from matches.view import match
from players.view import player
from teams.view import team

app = Robyn(__file__)


@app.startup_handler
async def startup_handler():
    print("Starting up")


@app.shutdown_handler
def shutdown_handler():
    print("Shutting down")


@app.get("/count", auth_required=True)
async def messages(request: Request):
    try:
        user = request.identity.claims["user"]
        count = await get_count_conn()
        return {"s": user, "c": count}
    except Exception as e:
        logger.error(f"Error in /count endpoint: {e}")
        return {"error": "Internal server error"}


@app.get("/")
async def index(request: Request):
    try:
        # await on_app_startup()
        auth_ = await check_headers_valid_email(request)
        context = {"request": request, "auth": auth_, "user": {}}
        template = templates.render_template(template_name="index.html", **context)
        return template
    except Exception as e:
        logger.error(f"Error in / endpoint: {e}")
        return "Internal server error"


@app.get("/test")
async def test():
    try:
        payload = {
            "email": 'asd@asd.asd',
            "scope": "email_verification",
        }
        token = create_access_token(payload)
        print(f"Encoded JWT Token: {token}")
        # Decode the JWT token
        decoded_data = decode_access_token(token)
        print(f"Decoded JWT Data: {decoded_data}")
    except Exception as e:
        logger.error(f"Error in /test endpoint: {e}")
        return {"error": "Internal server error"}


def main():
    try:
        app.add_directory(
            route="/static/",
            directory_path=os.path.join(BASE_DIR, "static"),
            index_file="",
        )
        app.add_response_header("server", "robyn")
        app.configure_authentication(BasicAuthHandler(token_getter=CustomBearerGetter()))
        app.include_router(auth)
        app.include_router(league)
        app.include_router(team)
        app.include_router(match)
        app.include_router(player)

        app.start(host='0.0.0.0', port=8081)
    except Exception as e:
        logger.error(f"Error during app startup: {e}")


if __name__ == "__main__":
    main()
