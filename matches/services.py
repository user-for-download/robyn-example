from typing import Any
from typing import Dict

from robyn import logger
from sqlalchemy import select, func, desc, or_, and_

from common.execute import update_or_create, get_or_create
from common.utils import int_to_abs, get_hero_info, scale_size, process_related_data
from config.db import Base, async_session
from config.settings import settings
from leagues.models import Series, League
from matches.models import Match, MatchPickBan, MatchPlayer
from players.services import save_player_instance


# heroes
async def create_node(hero_id: int, count: int, min_count: int, max_count: int) -> Dict[str, Any]:
    hero_name, hero_image = get_hero_info(hero_id)
    return {
        "id": hero_id,
        "name": hero_name,
        "count": count,
        "image": hero_image,
        "size": scale_size(count, min_count, max_count),
    }


async def get_hero_counts_picks_bans(type_: str, id_: int):
    try:
        async with async_session() as session:
            if type_ == 'team':
                match_filter = or_(
                    and_(Match.radiant_team_id == id_, MatchPickBan.is_radiant.is_(True)),
                    and_(Match.dire_team_id == id_, MatchPickBan.is_radiant.is_(False))
                )
            elif type_ == 'league':
                match_filter = and_(Match.league_id == id_)
            elif type_ == 'player':
                match_filter = and_(True)
            else:
                match_filter = and_(True)

            stmt = (
                select(MatchPickBan.hero_id, MatchPickBan.is_pick, func.count(MatchPickBan.hero_id).label('count'))
                .join(Match)
                .filter(Match.deleted_at.is_(None), MatchPickBan.deleted_at.is_(None))
                .filter(Match.game_version_id >= settings.GAME_VERSION)
                .filter(match_filter)
                .group_by(MatchPickBan.hero_id)
                .group_by(MatchPickBan.is_pick)
                .order_by(desc('count'))
            )

            result = await session.execute(stmt)
            pick_bans = result.all()

            nodes_picks = [
                await create_node(pick[0], pick[2], 0, 100)
                for pick in pick_bans if pick[1]
            ]

            nodes_bans = [
                await create_node(pick[0], pick[2], 0, 100)
                for pick in pick_bans if pick[1] is False
            ]

            return {
                "nodes_picks": nodes_picks,
                "links_picks": [],
                "nodes_bans": nodes_bans,
                "links_bans": [],
            }
    except Exception as e:
        logger.error("get_hero_counts_picks_bans: %s", e)
        return {}


async def get_hero_counts_picks_for_player(id_: int):
    try:
        async with async_session() as session:
            stmt = (
                select(MatchPlayer.hero_id, func.count(MatchPlayer.hero_id).label('count'))
                .filter(MatchPlayer.deleted_at.is_(None), MatchPlayer.steam_account_id == id_)
                .group_by(MatchPlayer.hero_id)
                .order_by(desc('count'))
            )

            result = await session.execute(stmt)
            picks = result.all()
            nodes_picks = [
                await create_node(pick[0], pick[1], 0, 100)
                for pick in picks if pick[0]
            ]

            return {
                "nodes_picks": nodes_picks,
                "links_picks": [],
                "nodes_bans": [],
                "links_bans": [],
            }
    except Exception as e:
        logger.error("get_hero_counts_picks_for_player: %s", e)
        return {}


# ------------
async def save_match(match_data: Dict[str, Any]) -> Base | None:
    try:
        match_id = match_data.get('id')

        defaults = {
            'id': match_id,
            "did_radiant_win": match_data.get("didRadiantWin", None),
            "duration_seconds": match_data.get("durationSeconds", None),
            "start_date_time": match_data.get("startDateTime", None),
            "tower_status_radiant": match_data.get("towerStatusRadiant", None),
            "tower_status_dire": match_data.get("towerStatusDire", None),
            "barracks_status_radiant": match_data.get(
                "barracksStatusRadiant", None
            ),
            "barracks_status_dire": match_data.get("barracksStatusDire", None),
            "cluster_id": match_data.get("clusterId", None),
            "first_blood_time": match_data.get("firstBloodTime", None),
            "lobby_type": match_data.get("lobbyType", None),
            "num_human_players": match_data.get("numHumanPlayers", None),
            "game_mode": match_data.get("gameMode", None),
            "replay_salt": match_data.get("replaySalt", None),
            "is_stats": match_data.get("isStats", None),
            "tournament_id": match_data.get("tournamentId", None),
            "tournament_round": match_data.get("tournamentRound", None),
            "average_rank": match_data.get("averageRank", None),
            "actual_rank": match_data.get("actualRank", None),
            "average_imp": match_data.get("averageImp", None),
            "parsed_date_time": match_data.get("parsedDateTime", None),
            "stats_date_time": match_data.get("statsDateTime", None),
            "league_id": match_data.get("leagueId", None),
            "radiant_team_id": int_to_abs(match_data, 'radiantTeamId'),
            "dire_team_id": int_to_abs(match_data, 'direTeamId'),
            "series_id": match_data.get("seriesId", None),
            "game_version_id": match_data.get("gameVersionId", None),
            "region_id": match_data.get("regionId", None),
            "sequence_num": match_data.get("sequenceNum", None),
            "rank": match_data.get("rank", None),
            "bracket": match_data.get("bracket", None),
            "end_date_time": match_data.get("endDateTime", None),
            "actual_rank_weight": match_data.get("actualRankWeight", None),
            "analysis_outcome": match_data.get("analysisOutcome", None),
            "predicted_outcome_weight": match_data.get(
                "predictedOutcomeWeight", None
            ),
            "bottom_lane_outcome": match_data.get("bottomLaneOutcome", None),
            "mid_lane_outcome": match_data.get("midLaneOutcome"),
            "top_lane_outcome": match_data.get("topLaneOutcome"),
            "radiant_networth_lead": match_data.get("radiantNetworthLead"),
            "radiant_experience_lead": match_data.get("radiantExperienceLead"),
            "radiant_kills": match_data.get("radiantKills"),
            "dire_kills": match_data.get("direKills"),
            "tower_status": match_data.get("towerStatus"),
            "lane_report": match_data.get("laneReport"),
            "win_rates": match_data.get("winRates"),
            "predicted_win_rates": match_data.get("predictedWinRates"),
            "tower_deaths": match_data.get("towerDeaths"),
            "chat_events": match_data.get("chatEvents"),
            "did_request_download": match_data.get("didRequestDownload"),
            "game_result": match_data.get("gameResult"),
        }
        async with async_session() as session:
            await get_or_create(session, Series, {}, id=match_data.get("seriesId", None))
            await get_or_create(session, League, {}, id=match_data.get("leagueId", None))
            match, _ = await update_or_create(session, Match, defaults, id=match_id)

        await process_related_data(match_data, "pickBans", save_match_pick_ban, match_id)
        await process_related_data(match_data, "players", save_match_player)
        return match
    except Exception as e:
        logger.error(f'An error occurred while saving Match: {e}')
        return None


async def save_match_pick_ban(pb_data: Dict[str, Any], match_id: int) -> None:
    try:
        order = pb_data.get("order")
        defaults = {
            "match_id": match_id,
            "order": order,
            "is_pick": pb_data.get("isPick"),
            "hero_id": pb_data.get("heroId"),
            "banned_hero_id": pb_data.get("bannedHeroId"),
            "is_radiant": pb_data.get("isRadiant"),
            "player_index": pb_data.get("playerIndex"),
            "was_banned_successfully": pb_data.get("wasBannedSuccessfully"),
            "base_win_rate": pb_data.get("baseWinRate"),
            "adjusted_win_rate": pb_data.get("adjustedWinRate"),
            "pick_probability": pb_data.get("pickProbability"),
            "is_captain": pb_data.get("isCaptain"),
        }
        async with async_session() as session:
            await update_or_create(session, MatchPickBan, defaults, match_id=match_id, order=order)
    except Exception as e:
        logger.error("Failed to save match pick ban: %s", e)


async def save_match_player(player_data: Dict[str, Any]) -> None:
    try:
        await save_player_instance(player_data.get("steamAccountId"))

        defaults = {
            "steam_account_id": player_data.get("steamAccountId"),
            "hero_id": player_data.get("heroId"),
            "is_radiant": player_data.get("isRadiant"),
            "num_kills": player_data.get("numKills"),
            "num_deaths": player_data.get("numDeaths"),
            "num_assists": player_data.get("numAssists"),
            "leaver_status": player_data.get("leaverStatus"),
            "num_last_hits": player_data.get("numLastHits"),
            "num_denies": player_data.get("numDenies"),
            "gold_per_minute": player_data.get("goldPerMinute"),
            "experience_per_minute": player_data.get("experiencePerMinute"),
            "level": player_data.get("level"),
            "gold": player_data.get("gold"),
            "gold_spent": player_data.get("goldSpent"),
            "hero_damage": player_data.get("heroDamage"),
            "tower_damage": player_data.get("towerDamage"),
            "party_id": player_data.get("partyId"),
            "is_random": player_data.get("isRandom"),
            "lane": player_data.get("lane"),
            "streak_prediction": player_data.get("streakPrediction"),
            "intentional_feeding": player_data.get("intentionalFeeding"),
            "role": player_data.get("role"),
            "imp": player_data.get("imp"),
            "award": player_data.get("award"),
            "item0_id": player_data.get("item0Id"),
            "item1_id": player_data.get("item1Id"),
            "item2_id": player_data.get("item2Id"),
            "item3_id": player_data.get("item3Id"),
            "item4_id": player_data.get("item4Id"),
            "item5_id": player_data.get("item5Id"),
            "backpack0_id": player_data.get("backpack0Id"),
            "backpack1_id": player_data.get("backpack1Id"),
            "backpack2_id": player_data.get("backpack2Id"),
            "behavior": player_data.get("behavior"),
            "hero_healing": player_data.get("heroHealing"),
            "roam_lane": player_data.get("roamLane"),
            "is_victory": player_data.get("isVictory"),
            "networth": player_data.get("networth"),
            "neutral0_id": player_data.get("neutral0Id"),
            "dota_plus_hero_xp": player_data.get("dotaPlusHeroXp"),
            "invisible_seconds": player_data.get("invisibleSeconds"),
            "match_player_stats": player_data.get("matchPlayerStats"),
            "is_dire": player_data.get("isDire"),
            "role_basic": player_data.get("roleBasic"),
            "position": player_data.get("position"),
            "base_slot": player_data.get("baseSlot"),
            "kda": player_data.get("kda"),
            "map_location_home_fountain": player_data.get(
                "mapLocationHomeFountain"
            ),
            "faction": player_data.get("faction"),
            "calculate_imp_lane": player_data.get("calculateImpLane"),
            "game_version_id": player_data.get("gameVersionId"),
            "stats": player_data.get("stats"),
            "playback_data": player_data.get("playbackData"),
            "abilities": player_data.get("abilities")
        }
        async with async_session() as session:
            match_player, _ = await update_or_create(
                session,
                MatchPlayer,
                defaults,
                match_id=player_data.get("matchId"),
                player_slot=player_data.get("playerSlot")
            )
    except Exception as e:
        logger.error(f'An error occurred while save match player: {e}')
        return None
