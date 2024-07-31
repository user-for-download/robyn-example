import json

from sqlalchemy import BigInteger, ForeignKey, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column, class_mapper

from common.constants import HEROES
from common.utils import unix_to_datetime, seconds_to_hours_minutes, sum_elements, unix_to_string, get_delta_time
from config.db import a_id, a_small_int, a_big_int, a_bool, a_json, Base, a_int, a_char
from leagues.models import Series, League
from teams.models import Team


class MatchPlayer(Base):
    __tablename__ = 'match_players'

    match_id: Mapped[a_big_int]
    player_slot: Mapped[a_int]
    hero_id: Mapped[a_int]
    is_radiant: Mapped[a_bool]
    num_kills: Mapped[a_int]
    num_deaths: Mapped[a_int]
    num_assists: Mapped[a_int]
    leaver_status: Mapped[a_int]
    num_last_hits: Mapped[a_int]
    num_denies: Mapped[a_int]
    gold_per_minute: Mapped[a_int]
    experience_per_minute: Mapped[a_int]
    level: Mapped[a_int]
    gold: Mapped[a_int]
    gold_spent: Mapped[a_int]
    hero_damage: Mapped[a_int]
    tower_damage: Mapped[a_int]
    party_id: Mapped[a_int]
    is_random: Mapped[a_bool]
    lane: Mapped[a_int]
    streak_prediction: Mapped[a_int]
    intentional_feeding: Mapped[a_bool]
    role: Mapped[a_int]
    imp: Mapped[a_int]
    award: Mapped[a_int]
    item0_id: Mapped[a_int]
    item1_id: Mapped[a_int]
    item2_id: Mapped[a_int]
    item3_id: Mapped[a_int]
    item4_id: Mapped[a_int]
    item5_id: Mapped[a_int]
    backpack0_id: Mapped[a_int]
    backpack1_id: Mapped[a_int]
    backpack2_id: Mapped[a_int]
    behavior: Mapped[a_int]
    hero_healing: Mapped[a_int]
    roam_lane: Mapped[a_int]
    abilities: Mapped[a_json]
    is_victory: Mapped[a_bool]
    networth: Mapped[a_int]
    neutral0_id: Mapped[a_int]
    additional_unit: Mapped[a_json]
    dota_plus_hero_xp: Mapped[a_int]
    invisible_seconds: Mapped[a_int]
    match_player_stats: Mapped[a_json]
    stats: Mapped[a_json]
    playback_data: Mapped[a_json]
    is_dire: Mapped[a_bool]
    role_basic: Mapped[a_int]
    position: Mapped[a_int]
    base_slot: Mapped[a_int]
    kda: Mapped[a_char]
    map_location_home_fountain: Mapped[a_int]
    faction: Mapped[a_int]
    calculate_imp_lane: Mapped[a_int]
    game_version_id: Mapped[a_int]

    steam_account_id = mapped_column(BigInteger, ForeignKey("steam_accounts.id"))
    steam_account = relationship("SteamAccount", foreign_keys=[steam_account_id])

    __table_args__ = (
        Index('ix_match_players_match_id', 'match_id'),
        Index('ix_match_players_steam_account_id', 'steam_account_id'),
        Index('ix_match_players_hero_id', 'hero_id'),
    )

    def __str__(self):
        return f" player {self.steam_account_id}={self.player_slot}"


class MatchPickBan(Base):
    __tablename__ = 'match_picks_ban'

    is_pick: Mapped[a_bool]
    hero_id: Mapped[a_small_int]
    order: Mapped[a_small_int]
    banned_hero_id: Mapped[a_small_int]
    is_radiant: Mapped[a_bool]
    player_index: Mapped[a_small_int]
    was_banned_successfully: Mapped[a_bool]
    base_win_rate: Mapped[a_small_int]
    adjusted_win_rate: Mapped[a_small_int]
    pick_probability: Mapped[a_small_int]
    is_captain: Mapped[a_bool]
    match_id = mapped_column(BigInteger, ForeignKey("matches.id"))

    match = relationship("Match", back_populates="pick_bans")

    __table_args__ = (
        Index('ix_match_picks_ban_match_id', 'match_id'),
        Index('ix_match_picks_ban_hero_id', 'hero_id'),
    )

    def __str__(self):
        return f"pick={self.is_pick}/hero_id={self.hero_id}-m_id={self.match_id}"

    def hero_image_url(self):
        url_image = "https://rb.binetc.site/static/images/heroes/npc_dota_hero_"
        hero_image_name = HEROES.get(self.hero_id, "default.png")
        return f"{url_image}{hero_image_name}"


class Match(Base):
    __tablename__ = 'matches'

    id: Mapped[a_id]
    did_radiant_win: Mapped[a_bool]
    duration_seconds: Mapped[a_big_int]
    start_date_time: Mapped[a_big_int]
    tower_status_radiant: Mapped[a_big_int]
    tower_status_dire: Mapped[a_big_int]
    barracks_status_radiant: Mapped[a_big_int]
    barracks_status_dire: Mapped[a_big_int]
    cluster_id: Mapped[a_big_int]
    first_blood_time: Mapped[a_small_int]
    lobby_type: Mapped[a_big_int]
    num_human_players: Mapped[a_big_int]
    game_mode: Mapped[a_big_int]
    replay_salt: Mapped[a_big_int]
    is_stats: Mapped[a_bool]
    tournament_id: Mapped[a_big_int]
    tournament_round: Mapped[a_big_int]
    average_rank: Mapped[a_big_int]
    actual_rank: Mapped[a_big_int]
    average_imp: Mapped[a_big_int]
    parsed_date_time: Mapped[a_big_int]
    stats_date_time: Mapped[a_big_int]
    game_version_id: Mapped[a_small_int]
    region_id: Mapped[a_big_int]
    sequence_num: Mapped[a_big_int]
    rank: Mapped[a_big_int]
    bracket: Mapped[a_big_int]
    end_date_time: Mapped[a_big_int]
    actual_rank_weight: Mapped[a_big_int]
    # playback_data = models.OneToOneField(
    #     MatchPlaybackData,
    #     on_delete=models.SET_NULL,
    #     related_name="match",
    #     blank=True,
    #     null=True,
    # )
    # spectators = models.ManyToManyField(MatchPlayerSpectator, blank=True)
    # players = models.ManyToManyField(MatchPlayer, blank=True)
    analysis_outcome: Mapped[a_big_int]
    predicted_outcome_weight: Mapped[a_big_int]
    bottom_lane_outcome: Mapped[a_big_int]
    mid_lane_outcome: Mapped[a_big_int]
    top_lane_outcome: Mapped[a_big_int]
    radiant_networth_lead: Mapped[a_json]
    radiant_experience_lead: Mapped[a_json]
    radiant_kills: Mapped[a_json]
    dire_kills: Mapped[a_json]
    tower_status: Mapped[a_json]
    lane_report: Mapped[a_json]
    win_rates: Mapped[a_json]
    predicted_win_rates: Mapped[a_json]
    tower_deaths: Mapped[a_json]
    chat_events: Mapped[a_json]
    did_request_download: Mapped[a_bool]
    game_result: Mapped[a_big_int]

    series_id = mapped_column(BigInteger, ForeignKey("series.id"))
    league_id = mapped_column(BigInteger, ForeignKey("leagues.id"))
    radiant_team_id = mapped_column(BigInteger, ForeignKey("teams.id"))
    dire_team_id = mapped_column(BigInteger, ForeignKey("teams.id"))

    radiant_team = relationship(Team, foreign_keys=[radiant_team_id])
    dire_team = relationship(Team, foreign_keys=[dire_team_id])
    league = relationship(League, foreign_keys=[league_id])
    series = relationship(Series, foreign_keys=[series_id], back_populates="matches")

    pick_bans = relationship(MatchPickBan, back_populates="match")

    __table_args__ = (
        Index('ix_matches_league_id', 'league_id'),
        Index('ix_matches_series_id', 'series_id'),
        Index('ix_matches_radiant_team_id', 'radiant_team_id'),
        Index('ix_matches_dire_team_id', 'dire_team_id'),
    )

    def __str__(self):
        return f"lg{self.id}/tr{self.radiant_team_id}-vs-td{self.dire_team_id}"

    def __repr__(self) -> str:
        db = {col.key: getattr(self, col.key) for col in class_mapper(self.__class__).columns}
        data = json.dumps(db, default=str)

        return data

    def get_absolute_url(self):
        return f"/match/{self.id}"

    def get_verbose_start_datetime(self):
        return unix_to_string(self.start_date_time)

    def get_verbose_end_date_time(self):
        last_match_dt = unix_to_datetime(self.end_date_time)
        return get_delta_time(last_match_dt)

    def get_verbose_duration_seconds(self):
        return seconds_to_hours_minutes(self.duration_seconds)

    def get_count_dire_kills(self):
        return sum_elements(self.dire_kills)

    def get_count_radiant_kills(self):
        return sum_elements(self.radiant_kills)
