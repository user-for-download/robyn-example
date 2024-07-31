"""Initial migration

Revision ID: fcc2c78b0772
Revises: 
Create Date: 2024-07-30 15:59:27.408524

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fcc2c78b0772'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('leagues',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('registration_period', sa.SmallInteger(), nullable=True),
    sa.Column('country', sa.String(length=240), nullable=True),
    sa.Column('venue', sa.String(length=240), nullable=True),
    sa.Column('private', sa.Boolean(), nullable=True),
    sa.Column('city', sa.String(length=240), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('has_live_matches', sa.Boolean(), nullable=True),
    sa.Column('tier', sa.SmallInteger(), nullable=True),
    sa.Column('tournament_url', sa.Text(), nullable=True),
    sa.Column('free_to_spectate', sa.Boolean(), nullable=True),
    sa.Column('is_followed', sa.Boolean(), nullable=True),
    sa.Column('last_match_date', sa.BigInteger(), nullable=True),
    sa.Column('pro_circuit_points', sa.SmallInteger(), nullable=True),
    sa.Column('banner', sa.String(length=240), nullable=True),
    sa.Column('stop_sales_time', sa.String(length=240), nullable=True),
    sa.Column('image_uri', sa.Text(), nullable=True),
    sa.Column('display_name', sa.String(length=240), nullable=True),
    sa.Column('end_datetime', sa.BigInteger(), nullable=True),
    sa.Column('name', sa.String(length=240), nullable=True),
    sa.Column('prize_pool', sa.BigInteger(), nullable=True),
    sa.Column('base_prize_pool', sa.BigInteger(), nullable=True),
    sa.Column('region', sa.SmallInteger(), nullable=True),
    sa.Column('start_datetime', sa.BigInteger(), nullable=True),
    sa.Column('status', sa.SmallInteger(), nullable=True),
    sa.Column('is_over', sa.Boolean(), nullable=True),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', 'uuid')
    )
    op.create_index(op.f('ix_leagues_id'), 'leagues', ['id'], unique=True)
    op.create_index('ix_leagues_is_over', 'leagues', ['is_over'], unique=False)
    op.create_index('ix_leagues_name', 'leagues', ['name'], unique=False)
    op.create_index(op.f('ix_leagues_uuid'), 'leagues', ['uuid'], unique=True)
    op.create_table('pro_steam_accounts',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=240), nullable=True),
    sa.Column('real_name', sa.String(length=240), nullable=True),
    sa.Column('fantasy_role', sa.Integer(), nullable=True),
    sa.Column('team_id', sa.BigInteger(), nullable=True),
    sa.Column('sponsor', sa.String(length=240), nullable=True),
    sa.Column('is_locked', sa.Boolean(), nullable=True),
    sa.Column('is_pro', sa.Boolean(), nullable=True),
    sa.Column('total_earnings', sa.BigInteger(), nullable=True),
    sa.Column('birthday', sa.String(length=240), nullable=True),
    sa.Column('romanized_real_name', sa.String(length=240), nullable=True),
    sa.Column('roles', sa.Integer(), nullable=True),
    sa.Column('aliases', sa.JSON(), nullable=True),
    sa.Column('statuses', sa.Integer(), nullable=True),
    sa.Column('twitter_link', sa.String(length=240), nullable=True),
    sa.Column('twitch_link', sa.String(length=240), nullable=True),
    sa.Column('instagram_link', sa.String(length=240), nullable=True),
    sa.Column('vk_link', sa.String(length=240), nullable=True),
    sa.Column('you_tube_link', sa.String(length=240), nullable=True),
    sa.Column('facebook_link', sa.String(length=240), nullable=True),
    sa.Column('weibo_link', sa.String(length=240), nullable=True),
    sa.Column('signature_heroes', sa.String(length=240), nullable=True),
    sa.Column('countries', sa.JSON(), nullable=True),
    sa.Column('ti_wins', sa.Integer(), nullable=True),
    sa.Column('is_ti_winner', sa.Boolean(), nullable=True),
    sa.Column('position', sa.Integer(), nullable=True),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', 'uuid')
    )
    op.create_index(op.f('ix_pro_steam_accounts_id'), 'pro_steam_accounts', ['id'], unique=True)
    op.create_index('ix_pro_steam_accounts_is_pro', 'pro_steam_accounts', ['is_pro'], unique=False)
    op.create_index(op.f('ix_pro_steam_accounts_uuid'), 'pro_steam_accounts', ['uuid'], unique=True)
    op.create_table('teams',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=240), nullable=True),
    sa.Column('tag', sa.String(length=240), nullable=True),
    sa.Column('date_created', sa.CHAR(length=20), nullable=True),
    sa.Column('is_pro', sa.Boolean(), nullable=True),
    sa.Column('is_locked', sa.Boolean(), nullable=True),
    sa.Column('country_code', sa.String(length=240), nullable=True),
    sa.Column('url', sa.String(length=240), nullable=True),
    sa.Column('logo', sa.String(length=240), nullable=True),
    sa.Column('base_logo', sa.String(length=240), nullable=True),
    sa.Column('banner_logo', sa.String(length=240), nullable=True),
    sa.Column('sponsor_logo', sa.String(length=240), nullable=True),
    sa.Column('win_count', sa.SmallInteger(), nullable=True),
    sa.Column('loss_count', sa.SmallInteger(), nullable=True),
    sa.Column('rank', sa.SmallInteger(), nullable=True),
    sa.Column('last_match_date_time', sa.BigInteger(), nullable=True),
    sa.Column('coach_steam_account_id', sa.BigInteger(), nullable=True),
    sa.Column('country_name', sa.String(length=240), nullable=True),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', 'uuid')
    )
    op.create_index(op.f('ix_teams_id'), 'teams', ['id'], unique=True)
    op.create_index('ix_teams_name', 'teams', ['name'], unique=False)
    op.create_index(op.f('ix_teams_uuid'), 'teams', ['uuid'], unique=True)
    op.create_table('users',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=30), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('file', sa.String(), nullable=True),
    sa.Column('email_verified', sa.Boolean(), nullable=False),
    sa.Column('privileged', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.Column('last_login_date', sa.DateTime(), nullable=True),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', 'uuid'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=True)
    op.create_index(op.f('ix_users_uuid'), 'users', ['uuid'], unique=True)
    op.create_table('series',
    sa.Column('league_id', sa.BigInteger(), nullable=True),
    sa.Column('team_one_id', sa.BigInteger(), nullable=True),
    sa.Column('team_two_id', sa.BigInteger(), nullable=True),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('type', sa.SmallInteger(), nullable=True),
    sa.Column('team_one_win_count', sa.SmallInteger(), nullable=True),
    sa.Column('team_two_win_count', sa.SmallInteger(), nullable=True),
    sa.Column('winning_team_id', sa.BigInteger(), nullable=True),
    sa.Column('last_match_date_time', sa.BigInteger(), nullable=True),
    sa.Column('losing_team_id', sa.BigInteger(), nullable=True),
    sa.Column('is_over', sa.Boolean(), nullable=True),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['league_id'], ['leagues.id'], ),
    sa.ForeignKeyConstraint(['team_one_id'], ['teams.id'], ),
    sa.ForeignKeyConstraint(['team_two_id'], ['teams.id'], ),
    sa.PrimaryKeyConstraint('id', 'uuid')
    )
    op.create_index(op.f('ix_series_id'), 'series', ['id'], unique=True)
    op.create_index('ix_series_is_over', 'series', ['is_over'], unique=False)
    op.create_index('ix_series_league_id', 'series', ['league_id'], unique=False)
    op.create_index('ix_series_team_one_id', 'series', ['team_one_id'], unique=False)
    op.create_index('ix_series_team_two_id', 'series', ['team_two_id'], unique=False)
    op.create_index(op.f('ix_series_uuid'), 'series', ['uuid'], unique=True)
    op.create_table('steam_accounts',
    sa.Column('pro_steam_account_id', sa.BigInteger(), nullable=True),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('last_active_time', sa.String(length=240), nullable=True),
    sa.Column('profile_uri', sa.String(length=240), nullable=True),
    sa.Column('real_name', sa.String(length=240), nullable=True),
    sa.Column('time_created', sa.BigInteger(), nullable=True),
    sa.Column('country_code', sa.CHAR(length=20), nullable=True),
    sa.Column('state_code', sa.CHAR(length=20), nullable=True),
    sa.Column('city_id', sa.Integer(), nullable=True),
    sa.Column('community_visible_state', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=240), nullable=True),
    sa.Column('last_log_off', sa.CHAR(length=20), nullable=True),
    sa.Column('avatar', sa.String(length=240), nullable=True),
    sa.Column('primary_clan_id', sa.BigInteger(), nullable=True),
    sa.Column('solo_rank', sa.Integer(), nullable=True),
    sa.Column('party_rank', sa.Integer(), nullable=True),
    sa.Column('is_dota_plus_subscriber', sa.Boolean(), nullable=True),
    sa.Column('dota_plus_original_start_date', sa.BigInteger(), nullable=True),
    sa.Column('is_anonymous', sa.Boolean(), nullable=True),
    sa.Column('is_stratz_public', sa.Boolean(), nullable=True),
    sa.Column('season_rank', sa.Integer(), nullable=True),
    sa.Column('season_leaderboard_rank', sa.Integer(), nullable=True),
    sa.Column('season_leaderboard_division_id', sa.Integer(), nullable=True),
    sa.Column('smurf_flag', sa.Integer(), nullable=True),
    sa.Column('smurf_check_date', sa.BigInteger(), nullable=True),
    sa.Column('last_match_date_time', sa.BigInteger(), nullable=True),
    sa.Column('last_match_region_id', sa.Integer(), nullable=True),
    sa.Column('dota_account_level', sa.Integer(), nullable=True),
    sa.Column('rank_shift', sa.Integer(), nullable=True),
    sa.Column('bracket', sa.Integer(), nullable=True),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['pro_steam_account_id'], ['pro_steam_accounts.id'], ),
    sa.PrimaryKeyConstraint('id', 'uuid')
    )
    op.create_index(op.f('ix_steam_accounts_id'), 'steam_accounts', ['id'], unique=True)
    op.create_index('ix_steam_accounts_pro_steam_account_id', 'steam_accounts', ['pro_steam_account_id'], unique=False)
    op.create_index(op.f('ix_steam_accounts_uuid'), 'steam_accounts', ['uuid'], unique=True)
    op.create_table('match_players',
    sa.Column('steam_account_id', sa.BigInteger(), nullable=True),
    sa.Column('match_id', sa.BigInteger(), nullable=True),
    sa.Column('player_slot', sa.Integer(), nullable=True),
    sa.Column('hero_id', sa.Integer(), nullable=True),
    sa.Column('is_radiant', sa.Boolean(), nullable=True),
    sa.Column('num_kills', sa.Integer(), nullable=True),
    sa.Column('num_deaths', sa.Integer(), nullable=True),
    sa.Column('num_assists', sa.Integer(), nullable=True),
    sa.Column('leaver_status', sa.Integer(), nullable=True),
    sa.Column('num_last_hits', sa.Integer(), nullable=True),
    sa.Column('num_denies', sa.Integer(), nullable=True),
    sa.Column('gold_per_minute', sa.Integer(), nullable=True),
    sa.Column('experience_per_minute', sa.Integer(), nullable=True),
    sa.Column('level', sa.Integer(), nullable=True),
    sa.Column('gold', sa.Integer(), nullable=True),
    sa.Column('gold_spent', sa.Integer(), nullable=True),
    sa.Column('hero_damage', sa.Integer(), nullable=True),
    sa.Column('tower_damage', sa.Integer(), nullable=True),
    sa.Column('party_id', sa.Integer(), nullable=True),
    sa.Column('is_random', sa.Boolean(), nullable=True),
    sa.Column('lane', sa.Integer(), nullable=True),
    sa.Column('streak_prediction', sa.Integer(), nullable=True),
    sa.Column('intentional_feeding', sa.Boolean(), nullable=True),
    sa.Column('role', sa.Integer(), nullable=True),
    sa.Column('imp', sa.Integer(), nullable=True),
    sa.Column('award', sa.Integer(), nullable=True),
    sa.Column('item0_id', sa.Integer(), nullable=True),
    sa.Column('item1_id', sa.Integer(), nullable=True),
    sa.Column('item2_id', sa.Integer(), nullable=True),
    sa.Column('item3_id', sa.Integer(), nullable=True),
    sa.Column('item4_id', sa.Integer(), nullable=True),
    sa.Column('item5_id', sa.Integer(), nullable=True),
    sa.Column('backpack0_id', sa.Integer(), nullable=True),
    sa.Column('backpack1_id', sa.Integer(), nullable=True),
    sa.Column('backpack2_id', sa.Integer(), nullable=True),
    sa.Column('behavior', sa.Integer(), nullable=True),
    sa.Column('hero_healing', sa.Integer(), nullable=True),
    sa.Column('roam_lane', sa.Integer(), nullable=True),
    sa.Column('abilities', sa.JSON(), nullable=True),
    sa.Column('is_victory', sa.Boolean(), nullable=True),
    sa.Column('networth', sa.Integer(), nullable=True),
    sa.Column('neutral0_id', sa.Integer(), nullable=True),
    sa.Column('additional_unit', sa.JSON(), nullable=True),
    sa.Column('dota_plus_hero_xp', sa.Integer(), nullable=True),
    sa.Column('invisible_seconds', sa.Integer(), nullable=True),
    sa.Column('match_player_stats', sa.JSON(), nullable=True),
    sa.Column('stats', sa.JSON(), nullable=True),
    sa.Column('playback_data', sa.JSON(), nullable=True),
    sa.Column('is_dire', sa.Boolean(), nullable=True),
    sa.Column('role_basic', sa.Integer(), nullable=True),
    sa.Column('position', sa.Integer(), nullable=True),
    sa.Column('base_slot', sa.Integer(), nullable=True),
    sa.Column('kda', sa.CHAR(length=20), nullable=True),
    sa.Column('map_location_home_fountain', sa.Integer(), nullable=True),
    sa.Column('faction', sa.Integer(), nullable=True),
    sa.Column('calculate_imp_lane', sa.Integer(), nullable=True),
    sa.Column('game_version_id', sa.Integer(), nullable=True),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['steam_account_id'], ['steam_accounts.id'], ),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index('ix_match_players_hero_id', 'match_players', ['hero_id'], unique=False)
    op.create_index('ix_match_players_match_id', 'match_players', ['match_id'], unique=False)
    op.create_index('ix_match_players_steam_account_id', 'match_players', ['steam_account_id'], unique=False)
    op.create_index(op.f('ix_match_players_uuid'), 'match_players', ['uuid'], unique=True)
    op.create_table('matches',
    sa.Column('series_id', sa.BigInteger(), nullable=True),
    sa.Column('league_id', sa.BigInteger(), nullable=True),
    sa.Column('radiant_team_id', sa.BigInteger(), nullable=True),
    sa.Column('dire_team_id', sa.BigInteger(), nullable=True),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('did_radiant_win', sa.Boolean(), nullable=True),
    sa.Column('duration_seconds', sa.BigInteger(), nullable=True),
    sa.Column('start_date_time', sa.BigInteger(), nullable=True),
    sa.Column('tower_status_radiant', sa.BigInteger(), nullable=True),
    sa.Column('tower_status_dire', sa.BigInteger(), nullable=True),
    sa.Column('barracks_status_radiant', sa.BigInteger(), nullable=True),
    sa.Column('barracks_status_dire', sa.BigInteger(), nullable=True),
    sa.Column('cluster_id', sa.BigInteger(), nullable=True),
    sa.Column('first_blood_time', sa.SmallInteger(), nullable=True),
    sa.Column('lobby_type', sa.BigInteger(), nullable=True),
    sa.Column('num_human_players', sa.BigInteger(), nullable=True),
    sa.Column('game_mode', sa.BigInteger(), nullable=True),
    sa.Column('replay_salt', sa.BigInteger(), nullable=True),
    sa.Column('is_stats', sa.Boolean(), nullable=True),
    sa.Column('tournament_id', sa.BigInteger(), nullable=True),
    sa.Column('tournament_round', sa.BigInteger(), nullable=True),
    sa.Column('average_rank', sa.BigInteger(), nullable=True),
    sa.Column('actual_rank', sa.BigInteger(), nullable=True),
    sa.Column('average_imp', sa.BigInteger(), nullable=True),
    sa.Column('parsed_date_time', sa.BigInteger(), nullable=True),
    sa.Column('stats_date_time', sa.BigInteger(), nullable=True),
    sa.Column('game_version_id', sa.SmallInteger(), nullable=True),
    sa.Column('region_id', sa.BigInteger(), nullable=True),
    sa.Column('sequence_num', sa.BigInteger(), nullable=True),
    sa.Column('rank', sa.BigInteger(), nullable=True),
    sa.Column('bracket', sa.BigInteger(), nullable=True),
    sa.Column('end_date_time', sa.BigInteger(), nullable=True),
    sa.Column('actual_rank_weight', sa.BigInteger(), nullable=True),
    sa.Column('analysis_outcome', sa.BigInteger(), nullable=True),
    sa.Column('predicted_outcome_weight', sa.BigInteger(), nullable=True),
    sa.Column('bottom_lane_outcome', sa.BigInteger(), nullable=True),
    sa.Column('mid_lane_outcome', sa.BigInteger(), nullable=True),
    sa.Column('top_lane_outcome', sa.BigInteger(), nullable=True),
    sa.Column('radiant_networth_lead', sa.JSON(), nullable=True),
    sa.Column('radiant_experience_lead', sa.JSON(), nullable=True),
    sa.Column('radiant_kills', sa.JSON(), nullable=True),
    sa.Column('dire_kills', sa.JSON(), nullable=True),
    sa.Column('tower_status', sa.JSON(), nullable=True),
    sa.Column('lane_report', sa.JSON(), nullable=True),
    sa.Column('win_rates', sa.JSON(), nullable=True),
    sa.Column('predicted_win_rates', sa.JSON(), nullable=True),
    sa.Column('tower_deaths', sa.JSON(), nullable=True),
    sa.Column('chat_events', sa.JSON(), nullable=True),
    sa.Column('did_request_download', sa.Boolean(), nullable=True),
    sa.Column('game_result', sa.BigInteger(), nullable=True),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['dire_team_id'], ['teams.id'], ),
    sa.ForeignKeyConstraint(['league_id'], ['leagues.id'], ),
    sa.ForeignKeyConstraint(['radiant_team_id'], ['teams.id'], ),
    sa.ForeignKeyConstraint(['series_id'], ['series.id'], ),
    sa.PrimaryKeyConstraint('id', 'uuid')
    )
    op.create_index('ix_matches_dire_team_id', 'matches', ['dire_team_id'], unique=False)
    op.create_index(op.f('ix_matches_id'), 'matches', ['id'], unique=True)
    op.create_index('ix_matches_league_id', 'matches', ['league_id'], unique=False)
    op.create_index('ix_matches_radiant_team_id', 'matches', ['radiant_team_id'], unique=False)
    op.create_index('ix_matches_series_id', 'matches', ['series_id'], unique=False)
    op.create_index(op.f('ix_matches_uuid'), 'matches', ['uuid'], unique=True)
    op.create_table('team_members',
    sa.Column('steam_account_id', sa.BigInteger(), nullable=True),
    sa.Column('team_id', sa.BigInteger(), nullable=True),
    sa.Column('first_match_id', sa.BigInteger(), nullable=True),
    sa.Column('first_match_date_time', sa.CHAR(length=20), nullable=True),
    sa.Column('last_match_id', sa.BigInteger(), nullable=True),
    sa.Column('last_match_date_time', sa.CHAR(length=20), nullable=True),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['steam_account_id'], ['steam_accounts.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index('ix_team_members_steam_account_id', 'team_members', ['steam_account_id'], unique=False)
    op.create_index('ix_team_members_team_id', 'team_members', ['team_id'], unique=False)
    op.create_index(op.f('ix_team_members_uuid'), 'team_members', ['uuid'], unique=True)
    op.create_table('match_picks_ban',
    sa.Column('match_id', sa.BigInteger(), nullable=True),
    sa.Column('is_pick', sa.Boolean(), nullable=True),
    sa.Column('hero_id', sa.SmallInteger(), nullable=True),
    sa.Column('order', sa.SmallInteger(), nullable=True),
    sa.Column('banned_hero_id', sa.SmallInteger(), nullable=True),
    sa.Column('is_radiant', sa.Boolean(), nullable=True),
    sa.Column('player_index', sa.SmallInteger(), nullable=True),
    sa.Column('was_banned_successfully', sa.Boolean(), nullable=True),
    sa.Column('base_win_rate', sa.SmallInteger(), nullable=True),
    sa.Column('adjusted_win_rate', sa.SmallInteger(), nullable=True),
    sa.Column('pick_probability', sa.SmallInteger(), nullable=True),
    sa.Column('is_captain', sa.Boolean(), nullable=True),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index('ix_match_picks_ban_hero_id', 'match_picks_ban', ['hero_id'], unique=False)
    op.create_index('ix_match_picks_ban_match_id', 'match_picks_ban', ['match_id'], unique=False)
    op.create_index(op.f('ix_match_picks_ban_uuid'), 'match_picks_ban', ['uuid'], unique=True)
    op.create_table('players',
    sa.Column('team_id', sa.UUID(), nullable=True),
    sa.Column('steam_account_id', sa.BigInteger(), nullable=True),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('last_region_id', sa.BigInteger(), nullable=True),
    sa.Column('last_match_date', sa.BigInteger(), nullable=True),
    sa.Column('language_codes', sa.JSON(), nullable=True),
    sa.Column('first_match_date', sa.BigInteger(), nullable=True),
    sa.Column('match_count', sa.BigInteger(), nullable=True),
    sa.Column('win_count', sa.BigInteger(), nullable=True),
    sa.Column('behavior_score', sa.Integer(), nullable=True),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['steam_account_id'], ['steam_accounts.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['team_members.uuid'], ),
    sa.PrimaryKeyConstraint('id', 'uuid')
    )
    op.create_index(op.f('ix_players_id'), 'players', ['id'], unique=True)
    op.create_index('ix_players_steam_account_id', 'players', ['steam_account_id'], unique=False)
    op.create_index('ix_players_team_id', 'players', ['team_id'], unique=False)
    op.create_index(op.f('ix_players_uuid'), 'players', ['uuid'], unique=True)
    op.create_table('player_badges',
    sa.Column('player_id', sa.BigInteger(), nullable=False),
    sa.Column('badge_id', sa.Integer(), nullable=True),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index(op.f('ix_player_badges_uuid'), 'player_badges', ['uuid'], unique=True)
    op.create_table('player_battle_pass',
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.Column('level', sa.Integer(), nullable=True),
    sa.Column('country_code', sa.CHAR(length=20), nullable=True),
    sa.Column('bracket', sa.Integer(), nullable=True),
    sa.Column('is_anonymous', sa.Boolean(), nullable=True),
    sa.Column('player_id', sa.BigInteger(), nullable=False),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index(op.f('ix_player_battle_pass_uuid'), 'player_battle_pass', ['uuid'], unique=True)
    op.create_table('player_names',
    sa.Column('name', sa.String(length=240), nullable=True),
    sa.Column('last_seen_date_time', sa.BigInteger(), nullable=True),
    sa.Column('player_id', sa.BigInteger(), nullable=False),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index(op.f('ix_player_names_uuid'), 'player_names', ['uuid'], unique=True)
    op.create_table('player_ranks',
    sa.Column('season_rank_id', sa.Integer(), nullable=True),
    sa.Column('as_of_date_time', sa.String(length=240), nullable=True),
    sa.Column('is_core', sa.Boolean(), nullable=True),
    sa.Column('rank', sa.Integer(), nullable=True),
    sa.Column('player_id', sa.BigInteger(), nullable=False),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index(op.f('ix_player_ranks_uuid'), 'player_ranks', ['uuid'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_player_ranks_uuid'), table_name='player_ranks')
    op.drop_table('player_ranks')
    op.drop_index(op.f('ix_player_names_uuid'), table_name='player_names')
    op.drop_table('player_names')
    op.drop_index(op.f('ix_player_battle_pass_uuid'), table_name='player_battle_pass')
    op.drop_table('player_battle_pass')
    op.drop_index(op.f('ix_player_badges_uuid'), table_name='player_badges')
    op.drop_table('player_badges')
    op.drop_index(op.f('ix_players_uuid'), table_name='players')
    op.drop_index('ix_players_team_id', table_name='players')
    op.drop_index('ix_players_steam_account_id', table_name='players')
    op.drop_index(op.f('ix_players_id'), table_name='players')
    op.drop_table('players')
    op.drop_index(op.f('ix_match_picks_ban_uuid'), table_name='match_picks_ban')
    op.drop_index('ix_match_picks_ban_match_id', table_name='match_picks_ban')
    op.drop_index('ix_match_picks_ban_hero_id', table_name='match_picks_ban')
    op.drop_table('match_picks_ban')
    op.drop_index(op.f('ix_team_members_uuid'), table_name='team_members')
    op.drop_index('ix_team_members_team_id', table_name='team_members')
    op.drop_index('ix_team_members_steam_account_id', table_name='team_members')
    op.drop_table('team_members')
    op.drop_index(op.f('ix_matches_uuid'), table_name='matches')
    op.drop_index('ix_matches_series_id', table_name='matches')
    op.drop_index('ix_matches_radiant_team_id', table_name='matches')
    op.drop_index('ix_matches_league_id', table_name='matches')
    op.drop_index(op.f('ix_matches_id'), table_name='matches')
    op.drop_index('ix_matches_dire_team_id', table_name='matches')
    op.drop_table('matches')
    op.drop_index(op.f('ix_match_players_uuid'), table_name='match_players')
    op.drop_index('ix_match_players_steam_account_id', table_name='match_players')
    op.drop_index('ix_match_players_match_id', table_name='match_players')
    op.drop_index('ix_match_players_hero_id', table_name='match_players')
    op.drop_table('match_players')
    op.drop_index(op.f('ix_steam_accounts_uuid'), table_name='steam_accounts')
    op.drop_index('ix_steam_accounts_pro_steam_account_id', table_name='steam_accounts')
    op.drop_index(op.f('ix_steam_accounts_id'), table_name='steam_accounts')
    op.drop_table('steam_accounts')
    op.drop_index(op.f('ix_series_uuid'), table_name='series')
    op.drop_index('ix_series_team_two_id', table_name='series')
    op.drop_index('ix_series_team_one_id', table_name='series')
    op.drop_index('ix_series_league_id', table_name='series')
    op.drop_index('ix_series_is_over', table_name='series')
    op.drop_index(op.f('ix_series_id'), table_name='series')
    op.drop_table('series')
    op.drop_index(op.f('ix_users_uuid'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_teams_uuid'), table_name='teams')
    op.drop_index('ix_teams_name', table_name='teams')
    op.drop_index(op.f('ix_teams_id'), table_name='teams')
    op.drop_table('teams')
    op.drop_index(op.f('ix_pro_steam_accounts_uuid'), table_name='pro_steam_accounts')
    op.drop_index('ix_pro_steam_accounts_is_pro', table_name='pro_steam_accounts')
    op.drop_index(op.f('ix_pro_steam_accounts_id'), table_name='pro_steam_accounts')
    op.drop_table('pro_steam_accounts')
    op.drop_index(op.f('ix_leagues_uuid'), table_name='leagues')
    op.drop_index('ix_leagues_name', table_name='leagues')
    op.drop_index('ix_leagues_is_over', table_name='leagues')
    op.drop_index(op.f('ix_leagues_id'), table_name='leagues')
    op.drop_table('leagues')
    # ### end Alembic commands ###