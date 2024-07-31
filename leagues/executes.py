from typing import Optional, List

from robyn import logger
from sqlalchemy import select
from sqlalchemy.orm import selectinload, with_loader_criteria

from config.db import async_session
from leagues.models import Series
from matches.models import Match, MatchPickBan
from teams.models import Team


async def execute_series_for_league(league_id: int) -> Optional[List[Series]]:
    try:
        series_stmt = (
            select(Series)
            .filter(Series.league_id == league_id)
            .order_by(Series.id.desc())
            .options(
                selectinload(Series.team_one),
                selectinload(Series.team_two),
                selectinload(Series.matches)
                .options(
                    selectinload(Match.radiant_team),
                    selectinload(Match.dire_team),
                    selectinload(Match.pick_bans)
                ),
                with_loader_criteria(Series, Series.deleted_at.is_(None)),
                with_loader_criteria(Match, Match.deleted_at.is_(None)),
                with_loader_criteria(Team, Team.deleted_at.is_(None)),
                with_loader_criteria(MatchPickBan, MatchPickBan.deleted_at.is_(None)),
            )
            .limit(20)
        )
        async with async_session() as session:
            result = await session.execute(series_stmt)
            series = result.scalars().all()

        return series
    except Exception as e:
        logger.error(f"An error occurred get_series_for_league: {e}")
        return None
