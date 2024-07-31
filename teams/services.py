from typing import Optional, Dict, Any

from robyn import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from common.execute import update_or_create, get_or_create
from common.urls import get_od_url_team_list, get_url_team, get_url_team_matches
from common.utils import fetch_data, process_related_data, save_data_if_exists
from config.db import async_session, Base
from matches.services import save_match
from players.models import SteamAccount, Player
from players.services import save_player_instance, save_pro_steam_acc, save_steam_acc
from teams.models import Team, TeamMember


# teams
async def get_and_save_teams():
    try:
        response = await fetch_data(get_od_url_team_list(), dict)
        await process_related_data(response, "rows", process_save_team)
    except Exception as e:
        logger.error(f"get_and_save_teams: An error occurred: {e}")


async def process_save_team(team_data: Dict[str, Any]) -> None:
    try:
        team_id = team_data.get('team_id')
        is_pro = True if team_data.get("rating") >= 1200 else False
        defaults = {
            "id": team_id,
            "name": team_data.get("name"),
            "tag": team_data.get("tag"),
            "is_pro": is_pro,
            "rank": team_data.get("rating"),
            "logo": team_data.get("go_url"),
            "banner_logo": team_data.get("bannerLogo"),
            "win_count": team_data.get("wins"),
            "loss_count": team_data.get("losses"),
            "last_match_date_time": team_data.get("last_match_time"),
        }
        async with async_session() as session:
            team, _ = await update_or_create(session, Team, defaults, id=team_id)
    except Exception as e:
        # await session.rollback()
        logger.error(f"process_save_team: Error processing member data: {e}")


async def get_and_save_team(team_id: int):
    try:
        team_data = await fetch_data(get_url_team(team_id), dict)
        if not team_data:
            return
        await save_team(team_data)
        await process_related_data(team_data, 'members', process_save_member_data)
        await update_players_team_membership(team_id)
        team_matches = await fetch_data(get_url_team_matches(team_id), list)
        if not team_matches:
            return
        await process_related_data({"matches": team_matches}, "matches", save_match)
    except Exception as e:
        logger.error(f"get_and_save_team: An error occurred: {e}")


async def process_save_member_data(member_data: Dict[str, Any]) -> None:
    try:
        account_data = member_data.get('steamAccount')
        steam_account_id = account_data.get("id")
        if steam_account_id:
            await save_player_instance(steam_account_id)
            await save_data_if_exists(member_data, 'steamAccount', save_steam_acc)
            await save_data_if_exists(account_data, 'proSteamAccount', save_pro_steam_acc)
            await save_team_member(member_data, steam_account_id)
    except Exception as e:
        logger.error(f"process_member_data: Error processing member data: {e}")


async def save_team(team_data: Dict[str, Any]) -> Optional[Base]:
    try:
        team_id = team_data.get("id")
        defaults = {
            "name": team_data.get("name"),
            "tag": team_data.get("tag"),
            "date_created": str(team_data.get("dateCreated")),
            "is_pro": team_data.get("isProfessional"),
            "logo": team_data.get("logo"),
            "banner_logo": team_data.get("bannerLogo"),
            "win_count": team_data.get("winCount"),
            "loss_count": team_data.get("lossCount"),
            "last_match_date_time": team_data.get("lastMatchDateTime"),
            "is_followed": team_data.get("isFollowed"),
            "country_name": team_data.get("countryName", ""),
        }
        async with async_session() as session:
            team, _ = await update_or_create(session, Team, defaults, id=team_id)
        return team
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to save team: {e}")
        return None


async def save_team_member(member_data: Dict[str, Any], steam_account_id: int) -> Optional[Base]:
    try:
        async with async_session() as session:
            team_id = member_data.get("teamId")
            team, _ = await get_or_create(session, Team, {}, id=team_id)
            steam_acc, _ = await get_or_create(session, SteamAccount, {}, id=steam_account_id)
            defaults_member = {
                "team": team,
                "steam_account": steam_acc,
                "first_match_id": member_data.get("firstMatchId"),
                "first_match_date_time": member_data.get("firstMatchDateTime"),
                "last_match_id": member_data.get("lastMatchId"),
                "last_match_date_time": member_data.get("lastMatchDateTime"),
            }
            team_member, _ = await update_or_create(session, TeamMember, defaults_member,
                                                    steam_account_id=steam_account_id,
                                                    team_id=member_data.get("teamId")
                                                    )
        return team_member
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to save team: {e}")
        return None


async def get_team_from_id(session: AsyncSession, team_id: int):
    try:
        stmt = (
            select(Team)
            .where(Team.id == team_id)
            .filter(Team.deleted_at.is_(None))
        )
        result = await session.execute(stmt)
        league = result.scalars().first()
        return league
    except Exception as e:
        logger.error(f"Failed to save player: {e}")
        return None


async def get_team_members(session: AsyncSession, team_id: int):
    try:
        stmt = (
            select(TeamMember)
            .where(TeamMember.team_id == team_id)
            .order_by(TeamMember.last_match_id.desc())
            .options(
                selectinload(TeamMember.team),
                selectinload(TeamMember.steam_account)
            )
        )
        result = await session.execute(stmt)

        members = result.scalars().all()
        return members
    except Exception as e:
        logger.error(f"Failed to save player: {e}")
        return None


async def update_players_team_membership(team_id: int):
    try:
        async with async_session() as session:
            stmt = (
                select(TeamMember)
                .where(TeamMember.team_id == team_id)
                .order_by(TeamMember.last_match_id.desc())
            )
            result = await session.execute(stmt)
            members = result.scalars().all()
            for member in members[:5]:
                await update_or_create(session, Player, {"team": member}, id=member.steam_account_id)
    except Exception as e:
        await session.rollback()
        logger.error(f"An error occurred update_team_members: {e}")
