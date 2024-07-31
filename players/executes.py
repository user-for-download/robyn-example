from typing import Optional

from robyn import logger
from sqlalchemy import select
from sqlalchemy.orm import selectinload, with_loader_criteria

from config.db import async_session
from players.models import Player, SteamAccount, BattlePass, Badge, Rank, Name, ProSteamAccount
from teams.models import Team, TeamMember


async def execute_player(player_id: int) -> Optional[Player]:
    try:
        stmt = (
            select(Player)
            .filter(Player.id == player_id)
            .options(
                selectinload(Player.battle_passes),
                selectinload(Player.badges),
                selectinload(Player.ranks),
                selectinload(Player.names),
                selectinload(Player.team).options(
                    selectinload(TeamMember.team)
                ),
                selectinload(Player.steam_account).options(
                    selectinload(SteamAccount.pro_steam_account)
                ),
                with_loader_criteria(Player, Player.deleted_at.is_(None)),
                with_loader_criteria(BattlePass, BattlePass.deleted_at.is_(None)),
                with_loader_criteria(Badge, Badge.deleted_at.is_(None)),
                with_loader_criteria(Rank, Rank.deleted_at.is_(None)),
                with_loader_criteria(Name, Name.deleted_at.is_(None)),
                with_loader_criteria(TeamMember, TeamMember.deleted_at.is_(None)),
                with_loader_criteria(Team, Team.deleted_at.is_(None)),
                with_loader_criteria(SteamAccount, SteamAccount.deleted_at.is_(None)),
                with_loader_criteria(ProSteamAccount, ProSteamAccount.deleted_at.is_(None))
            )

        )
        async with async_session() as session:
            result = await session.execute(stmt)
            pl = result.scalars().first()
        return pl
    except Exception as e:
        logger.error(f"An error occurred get_series_for_league: {e}")
        return None
