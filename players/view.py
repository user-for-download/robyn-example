import asyncio

from robyn import SubRouter, Request, logger, jsonify
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from account.token import auth_required, check_headers_valid_email
from common.utils import parse_int, redirect_response, not_found_response
from config.db import async_session
from config.settings import templates
from players.executes import execute_player
from players.models import Player, SteamAccount
from players.services import get_and_save_player, get_and_save_pro_players

player = SubRouter(__name__, prefix="/player")


@player.get("/")
async def index():
    return redirect_response('/player/list')


@player.get("/list")
async def get_players_list(request: Request):
    auth = await check_headers_valid_email(request)
    stmt = (
        select(Player)
        .filter(Player.deleted_at.is_(None))
        .order_by(Player.last_match_date.desc())
        .options(
            selectinload(Player.steam_account)
            .options(
                selectinload(SteamAccount.pro_steam_account)
            ))
        .limit(50)
    )
    async with async_session() as session:
        result = await session.execute(stmt)
        players = result.scalars().all()
    template = "/players/list.html"
    context = {"request": request, "players": players, "auth": auth, "user": {}}
    template = templates.render_template(template, **context)
    return template


@player.post("/update")
@auth_required()
async def update_players(request: Request):
    try:
        asyncio.ensure_future(get_and_save_pro_players())
        return redirect_response('/player/list')
    except Exception as e:
        logger.error(f"update_players: {e}")
        return jsonify("Failed update players list: %s", e)


@player.get("/:player_id")
async def get_player(request: Request):
    auth = await check_headers_valid_email(request)
    player_id = await parse_int(request.path_params["player_id"])
    if player_id is None:
        return not_found_response(request, 'player', player_id)
    player_ = await execute_player(player_id)

    template = "/players/detail.html"
    context = {"request": request, "player": player_, "auth": auth, "user": {}}
    template = templates.render_template(template, **context)
    return template


@player.post("/:player_id/u")
@auth_required()
async def update_player(request):
    try:
        player_id = await parse_int(request.path_params.get("player_id"))
        asyncio.ensure_future(get_and_save_player(player_id))
        return redirect_response(f'/player/{player_id}')
    except Exception as e:
        logger.error(f"e_player: {e}")
        return jsonify("Failed update player list: %s", e)
