import asyncio

from robyn import SubRouter, Request, jsonify, logger
from sqlalchemy import select

from account.token import check_headers_valid_email, auth_required
from common.utils import parse_int, redirect_response, not_found_response
from config.db import async_session
from config.settings import templates
from leagues.executes import execute_series_for_league
from leagues.models import League
from leagues.services import get_and_save_leagues, get_and_save_league_series, check_and_save_leagues_data

league = SubRouter(__name__, prefix="/league")


@league.get("/")
async def index():
    return redirect_response('/league/list')


@league.get("/list")
async def get_league_list(request: Request):
    try:
        auth = await check_headers_valid_email(request)
        async with (async_session() as session):
            stmt = (
                select(League)
                .filter(League.deleted_at.is_(None), League.tier >= 2)
                .order_by(League.id.desc())
            )
            result = await session.execute(stmt)
            leagues = result.scalars().all()
        template = "/leagues/list.html"
        context = {"request": request, "leagues": leagues, "auth": auth, "user": {}}
        template = templates.render_template(template, **context)
        return template
    except Exception as e:
        return jsonify("Failed get league list: %s", e)


@league.post("/update")
@auth_required()
async def update_leagues(request: Request):
    try:
        asyncio.ensure_future(get_and_save_leagues())
        return redirect_response('/league/list')
    except Exception as e:
        logger.error(f"update_leagues: {e}")
        return jsonify("Failed update league list: %s", e)


@league.get("/all")
@auth_required()
async def update_all_leagues(request: Request):
    try:
        await check_and_save_leagues_data()
        return redirect_response('/league/list')
    except Exception as e:
        return jsonify("Failed update league list: %s", e)


@league.get("/:league_id")
async def get_league(request: Request):
    try:
        auth = await check_headers_valid_email(request)
        league_id = await parse_int(request.path_params["league_id"])
        if league_id is None:
            return not_found_response(request, 'league', league_id)

        league_stmt = (
            select(League)
            .where(League.id == league_id)
            .filter(League.deleted_at.is_(None))
        )
        async with async_session() as session:
            result = await session.execute(league_stmt)
            league_obj = result.scalars().first()
            if not league_obj:
                return {"NoResultFound league": league_id}

        series = await execute_series_for_league(league_id)

        teams = set()
        for series_obj in series:
            teams.add(series_obj.team_one)
            teams.add(series_obj.team_two)

        template = "/leagues/detail.html"
        context = {"request": request, "league": league_obj, "series": series, "teams": teams, "auth": auth,
                   "user": {}}
        template = templates.render_template(template, **context)
        return template
    except Exception as e:
        logger.error("get_league: %s", e)
        return jsonify("get_league: %s", e)


@league.post("/:league_id/u")
@auth_required()
async def update_league_series(request):
    try:
        league_id = await parse_int(request.path_params["league_id"])
        if league_id is None:
            return redirect_response(f'/league/list')
        asyncio.ensure_future(get_and_save_league_series(league_id))
        return redirect_response(f'/league/{league_id}')
    except Exception as e:
        logger.error("update_league_series: %s", e)
