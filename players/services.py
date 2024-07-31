from typing import Dict, Any, Optional

from robyn import logger
from sqlalchemy.exc import SQLAlchemyError

from common.execute import update_or_create, get_or_create
from common.urls import get_url_player, get_url_pro_steam_acc
from common.utils import fetch_data, process_related_data, save_data_if_exists
from config.db import Base, async_session
from players.models import ProSteamAccount, SteamAccount, Player, Badge, Rank, Name, BattlePass
from teams.models import TeamMember, Team


async def save_player_instance(player_id: int) -> Optional[Player]:
    try:
        async with async_session() as session:
            pro_steam_account = await get_or_create(session, ProSteamAccount, id=player_id)
            if not pro_steam_account:
                pro_steam_account = ProSteamAccount(id=player_id)
                session.add(pro_steam_account)

            steam_account = await get_or_create(session, SteamAccount, id=player_id)
            if not steam_account:
                steam_account = SteamAccount(id=player_id)
                steam_account.pro_steam_account_id = player_id
                session.add(steam_account)

            player = await get_or_create(session, Player, id=player_id)
            if not player:
                player = Player(id=player_id)
                player.steam_account_id = player_id
                session.add(player)

            await session.commit()
            return player

    except SQLAlchemyError as e:
        logger.error("Failed to save player instance: %s", e)
        await session.rollback()
        return None


async def save_pro_steam_acc(pro_data: Dict[str, Any]) -> Optional[Base]:
    try:
        async with async_session() as session:
            defaults_pro = {
                'name': pro_data.get('name'),
                'real_name': pro_data.get('realName'),
                'fantasy_role': pro_data.get('fantasyRole'),
                'team_id': pro_data.get('teamId'),
                'sponsor': pro_data.get('sponsor'),
                'is_locked': pro_data.get('isLocked'),
                'is_pro': pro_data.get('isPro'),
                'total_earnings': pro_data.get('totalEarnings'),
                'birthday': pro_data.get('birthday'),
                'romanized_real_name': pro_data.get('romanizedRealName'),
                'roles': pro_data.get('roles'),
                'statuses': pro_data.get('statuses'),
                'countries': pro_data.get('countries'),
                'aliases': pro_data.get('aliases'),
                'ti_wins': pro_data.get('tiWins'),
                'is_ti_winner': pro_data.get('istiwinner'),
                'position': pro_data.get('position'),
                'twitter_link': pro_data.get('twitterLink'),
                'twitch_link': pro_data.get('twitchLink'),
                'instagram_link': pro_data.get('instagramLink'),
                'vk_link': pro_data.get('vkLink'),
                'you_tube_link': pro_data.get('youTubeLink'),
                'facebook_link': pro_data.get('facebookLink'),
                'weibo_link': pro_data.get('weiboLink'),
                'signature_heroes': pro_data.get('signatureHeroes'),
            }
            pro_acc, _ = await update_or_create(session, ProSteamAccount, defaults_pro,
                                                id=pro_data.get('steamAccountId'))
            return pro_acc
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to save_pro_steam_acc: {e}")
        return None


async def save_steam_acc(steam_data: Dict[str, Any]) -> Optional[Base]:
    try:
        async with async_session() as session:
            steam_account_id = steam_data.get('id')
            defaults_acc = {
                'pro_steam_account_id': steam_account_id,
                'last_active_time': steam_data.get('lastActiveTime'),
                'id': steam_data.get('id'),
                'profile_uri': steam_data.get('profileUri'),
                'real_name': steam_data.get('realName'),
                'time_created': steam_data.get('timeCreated'),
                'country_code': steam_data.get('countryCode'),
                'state_code': steam_data.get('stateCode'),
                'city_id': steam_data.get('cityId'),
                'community_visible_state': steam_data.get('communityVisibleState'),
                'name': steam_data.get('name'),
                'avatar': steam_data.get('avatar'),
                'primary_clan_id': steam_data.get('primaryClanId'),
                'solo_rank': steam_data.get('soloRank'),
                'party_rank': steam_data.get('partyRank'),
                'is_dota_plus_subscriber': steam_data.get('isDotaPlusSubscriber', False),
                'dota_plus_original_start_date': steam_data.get('dotaPlusOriginalStartDate'),
                'is_anonymous': steam_data.get('isAnonymous', False),
                'is_stratz_public': steam_data.get('isStratzPublic', False),
                'season_rank': steam_data.get('seasonRank'),
                'season_leaderboard_rank': steam_data.get('seasonLeaderboardRank'),
                'season_leaderboard_division_id': steam_data.get('seasonLeaderboardDivisionId'),
                'smurf_flag': steam_data.get('smurfFlag', False),
                'smurf_check_date': steam_data.get('smurfCheckDate'),
                'last_match_date_time': steam_data.get('lastMatchDateTime'),
                'last_match_region_id': steam_data.get('lastMatchRegionId'),
                'dota_account_level': steam_data.get('dotaAccountLevel'),
                'rank_shift': steam_data.get('rankShift', 0)
            }
            pro_acc, _ = await update_or_create(session, SteamAccount, defaults_acc, id=steam_account_id)
            return pro_acc
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to save_pro_steam_acc: {e}")
        return None


async def get_and_save_player(player_id: int):
    try:
        player_data = await fetch_data(get_url_player(player_id), dict)
        if not player_data:
            return
        player_id = player_data.get("steamAccountId")
        account_data = player_data.get('steamAccount')
        team_member = player_data.get('team')

        await save_player_instance(player_id)
        player = await save_player(player_data)
        await save_data_if_exists(player_data, 'steamAccount', save_steam_acc)
        await save_data_if_exists(account_data, 'proSteamAccount', save_pro_steam_acc)
        if team_member:
            await save_player_team_member(team_member, player_id)
        if player:
            await process_related_data(player_data, "badges", save_player_badge, player_id)
            await process_related_data(player_data, "ranks", save_player_rank, player_id)
            await process_related_data(player_data, "battlePass", save_player_battle_pass, player_id)
            await process_related_data(player_data, "names", save_player_names, player_id)
        return
    except Exception as e:
        logger.error(f"get_and_save_player: An error occurred: {e}")


async def save_player(player_data: Dict[str, Any]) -> Optional[Base]:
    try:
        async with async_session() as session:
            player_id = player_data.get("steamAccountId")
            defaults = {
                'steam_account_id': player_id,
                'last_match_date': player_data.get('date'),
                'last_region_id': player_data.get('lastRegionId'),
                'first_match_date': player_data.get('firstMatchDate'),
                'match_count': player_data.get('matchCount'),
                'win_count': player_data.get('winCount'),
                'behavior_score': player_data.get('behaviorScore'),
                'language_codes': player_data.get('languageCode'),
            }
            player, _ = await update_or_create(session, Player, defaults, id=player_id)
            return player
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to save player: {e}")
        return None


async def save_player_rank(rank_data: Dict[str, Any], player_id: int) -> Optional[Base]:
    try:
        async with async_session() as session:
            defaults = {
                "as_of_date_time": rank_data.get('asOfDateTime'),
                "rank": rank_data.get('rank'),
                "is_core": rank_data.get('isCore'),
            }
        rank, _ = await update_or_create(session, Rank, defaults,
                                         player_id=player_id,
                                         season_rank_id=rank_data.get('seasonRankId'))
        return rank
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to save player rank: {e}")
        return None


async def save_player_names(name_data: Dict[str, Any], player_id: int) -> Optional[Base]:
    try:
        async with async_session() as session:
            defaults = {
                "name": name_data.get('name'),
                "last_seen_date_time": name_data.get('lastseendatetime'),
            }
            rank, _ = await update_or_create(session, Name, defaults,
                                             player_id=player_id,
                                             name=name_data.get('name'))
            return rank
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to save player Names: {e}")
        return None


async def save_player_battle_pass(battle_data: Dict[str, Any], player_id: int) -> Optional[Base]:
    try:
        async with async_session() as session:
            defaults = {
                "level": battle_data.get('level'),
                "country_code": battle_data.get('countryCode'),
                "bracket": battle_data.get('bracket'),
                "is_anonymous": battle_data.get('isAnonymous'),
            }
            rank, _ = await update_or_create(session, BattlePass, defaults,
                                             player_id=player_id,
                                             event_id=battle_data.get('eventId'))
            return rank
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to save player BattlePass: {e}")
        return None


async def save_player_badge(badge_data: Dict[str, Any], player_id: int) -> Optional[Base]:
    try:
        async with async_session() as session:
            defaults = {
                "badge_id": badge_data.get('badge_id'),
            }
            rank, _ = await update_or_create(session, Badge, defaults, player_id=player_id)
            return rank
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to save player badge: {e}")
        return None


async def save_player_team_member(team_data: Dict[str, Any], player_id: int) -> Optional[Base]:
    try:
        team_id = team_data.get("teamId")
        async with async_session() as session:
            defaults_member = {
                "team_id": team_id,
                "steam_account_id": player_id,
                "first_match_id": team_data.get("firstMatchId"),
                "first_match_date_time": team_data.get("firstMatchDateTime"),
                "last_match_id": team_data.get("lastMatchId"),
                "last_match_date_time": team_data.get("lastMatchDateTime"),
            }
            team, _ = await get_or_create(session, Team, {}, id=team_id)
            team_member, _ = await update_or_create(
                session, TeamMember, defaults_member,
                steam_account_id=player_id,
                team_id=team_id
            )
        await update_or_create(session, Player, {"team": team_member}, id=player_id)
        return team_member
    except Exception as e:
        logger.error(f"Failed to save player team member: {e}")
        return None


async def get_and_save_pro_players():
    try:
        players = await fetch_data(get_url_pro_steam_acc(), dict)
        for player_id, player_data in players.items():
            await save_player_instance(int(player_id))
            await save_steam_acc(
                {"id": int(player_id), "real_name": player_data.get('realName'), "name": player_data.get('name')})
            await save_pro_steam_acc(player_data)
        logger.info(f"players count:{len(players)}")
    except Exception as e:
        logger.error(f"get_and_save_pro_players: An error occurred: {e}")
