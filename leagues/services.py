from datetime import timedelta
from typing import Dict, Any, Optional

from robyn import logger
from sqlalchemy import update, select, or_

from common.execute import get_or_create, update_or_create
from common.urls import get_url_league_list, get_url_league_series_list
from common.utils import (
    int_to_abs,
    date_as_number,
    now_tz,
    fetch_data,
    process_related_data, process_entities,
)
from config.db import Base, async_session
from leagues.models import League, Series
from matches.services import save_match
from teams.models import Team


# leagues
async def get_and_save_leagues():
    try:
        leagues = await fetch_data(get_url_league_list(), list)
        await process_related_data({"leagues": leagues}, "leagues", save_league)
        await update_is_over_league()
    except Exception as e:
        logger.error(f"get_and_save_leagues: An error occurred: {e}")


async def save_league(league_data: Dict[str, Any]) -> Base | None:
    try:
        defaults = {
            "id": league_data.get("id"),
            "registration_period": league_data.get("registrationPeriod"),
            "country": league_data.get("country"),
            "venue": league_data.get("venue"),
            "private": league_data.get("private"),
            "city": league_data.get("city"),
            "description": league_data.get("description"),
            "has_live_matches": league_data.get("hasLiveMatches"),
            "tier": league_data.get("tier"),
            "tournament_url": league_data.get("tournamentUrl"),
            "free_to_spectate": league_data.get("freeToSpectate"),
            "is_followed": league_data.get("isFollowed"),
            "pro_circuit_points": league_data.get("proCircuitPoints"),
            "banner": league_data.get("banner"),
            "stop_sales_time": league_data.get("stopSalesTime"),
            "image_uri": league_data.get("imageUri"),
            "display_name": league_data.get("displayName"),
            "end_datetime": league_data.get("endDateTime"),
            "name": league_data.get("name"),
            "prize_pool": league_data.get("prizePool"),
            "base_prize_pool": league_data.get("basePrizePool"),
            "region": league_data.get("region"),
            "start_datetime": league_data.get("startDateTime"),
            "status": league_data.get("status"),
        }
        async with async_session() as session:
            league, created = await update_or_create(
                session, League, defaults, id=league_data.get("id")
            )
        return league
    except Exception as e:
        session.rollback()
        logger.error(f"An error occurred while saving League: {e}")
        return None


async def update_is_over_league():
    try:
        stmt = (
            update(League)
            .filter(
                League.end_datetime < date_as_number(),
                League.deleted_at.is_(None),
            )
            .filter(League.is_over.is_(False) | League.is_over.is_(None))
            .values(is_over=True)
        )
        async with async_session() as session:
            # Execute the update statement
            await session.execute(stmt)

            # Commit the transaction
            await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"An error occurred update_is_over_league: {e}")
        return None


async def check_and_save_leagues_data():
    try:
        await update_is_over_league()
        async with (async_session() as session):
            stmt = (
                select(League.id)
                .filter(League.deleted_at.is_(None), League.tier >= 2)
                .filter(League.is_over.is_(False) | League.is_over.is_(None))
                .order_by(League.id.desc())
            )
            result = await session.execute(stmt)
            league_ids = result.scalars().all()
            logger.info(league_ids)

        await process_entities(league_ids, get_and_save_league_series, "league")
    except Exception as e:
        logger.error(f"get_and_save_all_data_leagues: An error occurred: {e}")


# league series
async def get_and_save_league_series(league_id: int):
    try:
        series = await fetch_data(get_url_league_series_list(league_id), list)
        await update_is_over_series()
        await process_related_data({"series": series}, "series", save_series)
    except Exception as e:
        logger.error(f"get_and_save_league_series: An error occurred: {e}")


async def save_series(series_data: Dict[str, Any]) -> Optional[Base]:
    try:
        series_id = series_data.get("id")
        team_one_id = int_to_abs(series_data, "teamOneId")
        team_two_id = int_to_abs(series_data, "teamTwoId")
        league_id = series_data.get("leagueId")
        async with async_session() as session:
            league, _ = await get_or_create(session, League, {}, id=league_id)
            team_one, _ = await get_or_create(
                session, Team, {"name": f"Team-{team_one_id}"}, id=team_one_id
            )
            team_two, _ = await get_or_create(
                session, Team, {"name": f"Team-{team_two_id}"}, id=team_two_id
            )
            defaults = {
                "league_id": league_id,
                "team_one_id": team_one_id,
                "team_two_id": team_two_id,
                "type": series_data.get("type"),
                "team_one_win_count": series_data.get("teamOneWinCount"),
                "team_two_win_count": series_data.get("teamTwoWinCount"),
                "winning_team_id": int_to_abs(series_data, "winningTeamId"),
                "last_match_date_time": series_data.get("lastMatchDate"),
            }
            series, _ = await update_or_create(session, Series, defaults, id=series_id)

        await process_related_data(series_data, "matches", save_match)
    except Exception as e:
        logger.error(f"Failed to save series: {e}")
        return None


async def update_is_over_series():
    try:
        stmt = (
            update(Series)
            .filter(
                Series.last_match_date_time
                < date_as_number(now_tz() - timedelta(hours=12)),
                Series.is_over.is_(False),
                Series.deleted_at.is_(None),
            )
            .values(is_over=True)
        )
        async with async_session() as session:
            # Execute the update statement
            await session.execute(stmt)

            # Commit the transaction
            await session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"An error occurred update_is_over_series: {e}")
        return None


async def get_leagues_for_team(team_id: int):
    try:
        stmt = (
            select(League)
            .join(Series)
            .filter(League.deleted_at.is_(None), Series.deleted_at.is_(None))
            .filter(or_(Series.team_one_id == team_id, Series.team_two_id == team_id))
            .distinct()
            .order_by(League.id.desc())
        )
        async with async_session() as session:
            result = await session.execute(stmt)
            leagues = result.scalars().all()

        return leagues
    except Exception as e:
        logger.error(f"An error occurred get_leagues_for_team: {e}")
        return None
