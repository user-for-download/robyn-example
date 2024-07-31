from robyn import SubRouter, Request, logger
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from account.token import check_headers_valid_email
from common.execute import active_random
from common.utils import redirect_response
from config.db import async_session
from config.settings import settings
from config.settings import templates
from matches.models import Match
from matches.services import get_hero_counts_picks_bans, get_hero_counts_picks_for_player

match = SubRouter(__name__, prefix="/match")


@match.get("/")
async def index():
    return redirect_response('/match/list')


@match.get("/list")
async def get_team_list(request: Request):
    try:
        auth = await check_headers_valid_email(request)
        matches_stmt = (
            select(Match)
            .filter(Match.deleted_at.is_(None))
            .filter(Match.game_version_id == settings.GAME_VERSION)
            .order_by(Match.id.desc())
            .options(
                selectinload(Match.radiant_team),
                selectinload(Match.dire_team),
                selectinload(Match.pick_bans)
            )
            .limit(50)
        )
        async with async_session() as session:
            result = await session.execute(matches_stmt)
            matches = result.scalars().all()
        template = "/matches/list.html"
        context = {"request": request, "matches": matches, "auth": auth, "user": {}}
        template = templates.render_template(template, **context)
        return template
    except Exception as e:
        logger.error("get_team_list: %s", e)
        await index()


@match.get("/:match_id")
async def get_team(request: Request):
    match_id = int(request.path_params.get("match_id"))
    async with async_session() as session:
        instance = await active_random(session, Match, id=match_id)
        if not instance:
            return {"NoResultFound match": match_id}
        return repr(instance)


@match.get("/picks")
async def get_picks(request: Request):
    try:
        query_data = request.query_params.to_dict()
        type_obj = query_data.get('type_obj')
        id_obj = query_data.get('id_obj')
        league_id = query_data.get('league_id')
        team_id = query_data.get('team_id')
        start_date_time = query_data.get('start_date_time')
        duration_seconds = query_data.get('duration_seconds')

        if not type_obj or not id_obj:
            return {"data": {'error': "Missing type_obj or id_obj parameter"}}

        filters = []
        if league_id:
            filters.append(Match.league_id == league_id)
        if team_id:
            filters.append(or_(Match.radiant_team_id == team_id, Match.dire_team_id == team_id))
        if start_date_time:
            filters.append(Match.start_date_time >= start_date_time)
        if duration_seconds:
            filters.append(Match.duration_seconds >= duration_seconds)

        if type_obj[0] == 'player':
            data = await get_hero_counts_picks_for_player(int(id_obj[0]))
        else:
            data = await get_hero_counts_picks_bans(type_obj[0], int(id_obj[0]))

        return data
    except Exception as e:
        return {"data": {'error': str(e)}}
