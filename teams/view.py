import asyncio

from robyn import SubRouter, Request, jsonify, logger
from sqlalchemy import select

from account.token import check_headers_valid_email, auth_required
from common.utils import redirect_response, parse_int, not_found_response
from config.db import async_session
from config.settings import templates
from leagues.services import get_leagues_for_team
from teams.models import Team
from teams.services import get_and_save_teams, get_team_from_id, get_and_save_team, get_team_members

team = SubRouter(__name__, prefix="/team")


@team.get("/")
async def index():
    return redirect_response('/team/list')


@team.get("/list")
async def get_team_list(request: Request):
    try:
        auth = await check_headers_valid_email(request)
        async with async_session() as session:
            stmt = (
                select(Team)
                .filter(Team.deleted_at.is_(None))
                .filter(Team.rank.is_not(None))
                .order_by(Team.rank.desc())
                .limit(30)
            )
            result = await session.execute(stmt)
            teams = result.scalars().all()
        template = "/teams/list.html"
        context = {"request": request, "teams": teams, "auth": auth, "user": {}}
        template = templates.render_template(template, **context)
        return template
    except Exception as e:
        return jsonify("Failed get league list: %s", e)


@team.post("/update")
@auth_required()
async def update_team_list(request: Request):
    try:
        asyncio.ensure_future(get_and_save_teams())
        return redirect_response('/team/list')
    except Exception as e:
        logger.error(f"update_team_list: {e}")
        return jsonify("Failed update team list: %s", e)


@team.get("/:team_id")
async def get_team(request):
    try:
        auth = await check_headers_valid_email(request)
        team_id = await parse_int(request.path_params["team_id"])
        if team_id is None:
            return not_found_response(request, 'team', team_id)

        async with async_session() as session:
            instance = await get_team_from_id(session, team_id)
            if not instance:
                return {"NoResultFound team": team_id}
            members = await get_team_members(session, team_id)

        leagues = await get_leagues_for_team(team_id)

        template = "/teams/detail.html"
        context = {"request": request, "team": instance, "leagues": leagues, "members": members, "auth": auth,
                   "user": {}}
        return templates.render_template(template, **context)
    except Exception as e:
        logger.error("get_team: %s", e)
        return jsonify("get_team: %s", e)


@team.post("/:team_id/u")
@auth_required()
async def update_team(request):
    try:
        team_id = await parse_int(request.path_params["team_id"])
        if team_id is None:
            return redirect_response(f'/team/list')
        asyncio.ensure_future(get_and_save_team(team_id))
        return redirect_response(f'/team/{team_id}')
    except Exception as e:
        logger.error("update_team: %s", e)
