import json

from sqlalchemy import ForeignKey, BigInteger, Index, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, class_mapper

from common.utils import unix_to_string, convert_to_datetime
from config.db import Base, a_id, a_char, a_str, a_int, a_bool, a_big_int, a_json


class BattlePass(Base):
    __tablename__ = 'player_battle_pass'

    event_id: Mapped[a_int]
    level: Mapped[a_int]
    country_code: Mapped[a_char]
    bracket: Mapped[a_int]
    is_anonymous: Mapped[a_bool]
    player_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('players.id'))

    player: Mapped["Player"] = relationship('Player', back_populates='battle_passes')


class Badge(Base):
    __tablename__ = 'player_badges'

    player_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('players.id'))
    badge_id: Mapped[a_int]

    player: Mapped["Player"] = relationship('Player', back_populates='badges')


class Rank(Base):
    __tablename__ = 'player_ranks'

    season_rank_id: Mapped[a_int]
    as_of_date_time: Mapped[a_str]
    is_core: Mapped[a_bool]
    rank: Mapped[a_int]
    player_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('players.id'))

    player: Mapped["Player"] = relationship('Player', back_populates='ranks')

    def __str__(self):
        return f"season:  {self.season_rank_id} at {convert_to_datetime(self.as_of_date_time)}"


class Name(Base):
    __tablename__ = 'player_names'

    name: Mapped[a_str]
    last_seen_date_time: Mapped[a_big_int]
    player_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('players.id'))

    player: Mapped["Player"] = relationship('Player', back_populates='names')

    def __str__(self):
        return f"{self.name}  / last at {unix_to_string(self.last_seen_date_time)}"


class ProSteamAccount(Base):
    __tablename__ = 'pro_steam_accounts'

    id: Mapped[a_id]
    name: Mapped[a_str]
    real_name: Mapped[a_str]
    fantasy_role: Mapped[a_int]
    team_id: Mapped[a_big_int]
    sponsor: Mapped[a_str]
    is_locked: Mapped[a_bool]
    is_pro: Mapped[a_bool]
    total_earnings: Mapped[a_big_int]
    birthday: Mapped[a_str]
    romanized_real_name: Mapped[a_str]
    roles: Mapped[a_int]
    aliases: Mapped[a_json]
    statuses: Mapped[a_int]
    twitter_link: Mapped[a_str]
    twitch_link: Mapped[a_str]
    instagram_link: Mapped[a_str]
    vk_link: Mapped[a_str]
    you_tube_link: Mapped[a_str]
    facebook_link: Mapped[a_str]
    weibo_link: Mapped[a_str]
    signature_heroes: Mapped[a_str]
    countries: Mapped[a_json]
    ti_wins: Mapped[a_int]
    is_ti_winner: Mapped[a_bool]
    position: Mapped[a_int]

    __table_args__ = (
        Index('ix_pro_steam_accounts_is_pro', 'is_pro'),
    )

    def __str__(self):
        return f"{self.real_name}"

    def get_absolute_url(self):
        return f"/steam/{self.id}/"


class SteamAccount(Base):
    __tablename__ = 'steam_accounts'

    id: Mapped[a_id]
    last_active_time: Mapped[a_str]
    profile_uri: Mapped[a_str]
    real_name: Mapped[a_str]
    time_created: Mapped[a_big_int]
    country_code: Mapped[a_char]
    state_code: Mapped[a_char]
    city_id: Mapped[a_int]
    community_visible_state: Mapped[a_int]
    name: Mapped[a_str]
    last_log_off: Mapped[a_char]
    avatar: Mapped[a_str]
    primary_clan_id: Mapped[a_big_int]
    solo_rank: Mapped[a_int]
    party_rank: Mapped[a_int]
    is_dota_plus_subscriber: Mapped[a_bool]
    dota_plus_original_start_date: Mapped[a_big_int]
    is_anonymous: Mapped[a_bool]
    is_stratz_public: Mapped[a_bool]
    season_rank: Mapped[a_int]
    season_leaderboard_rank: Mapped[a_int]
    season_leaderboard_division_id: Mapped[a_int]
    smurf_flag: Mapped[a_int]
    smurf_check_date: Mapped[a_big_int]
    last_match_date_time: Mapped[a_big_int]
    last_match_region_id: Mapped[a_int]
    dota_account_level: Mapped[a_int]
    rank_shift: Mapped[a_int]
    bracket: Mapped[a_int]

    pro_steam_account_id = mapped_column(BigInteger, ForeignKey("pro_steam_accounts.id"))
    pro_steam_account = relationship("ProSteamAccount", foreign_keys=[pro_steam_account_id])

    __table_args__ = (
        Index('ix_steam_accounts_pro_steam_account_id', 'pro_steam_account_id'),
    )

    def __str__(self):
        return f"{self.name}"

    def get_real_name(self):
        name = self.pro_steam_account.real_name if (self.pro_steam_account
                                                    and self.pro_steam_account.real_name) \
            else f"{self.id}"
        return f"{name}"

    def get_verbose_last_match_date_time(self):
        return unix_to_string(self.last_match_date_time)


class Player(Base):
    __tablename__ = 'players'

    id: Mapped[a_id]
    battle_passes = relationship("BattlePass", back_populates="player")
    badges = relationship("Badge", back_populates="player")
    ranks = relationship("Rank", back_populates="player")
    names = relationship("Name", back_populates="player")
    last_region_id: Mapped[a_big_int]
    last_match_date: Mapped[a_big_int]
    language_codes: Mapped[a_json]
    first_match_date: Mapped[a_big_int]
    match_count: Mapped[a_big_int]
    win_count: Mapped[a_big_int]
    behavior_score: Mapped[a_int]
    team_id = mapped_column(UUID, ForeignKey("team_members.uuid"))
    steam_account_id = mapped_column(BigInteger, ForeignKey("steam_accounts.id"))

    team = relationship("TeamMember", foreign_keys=[team_id])
    steam_account = relationship("SteamAccount", foreign_keys=[steam_account_id])

    __table_args__ = (
        Index('ix_players_team_id', 'team_id'),
        Index('ix_players_steam_account_id', 'steam_account_id'),
    )

    # def __str__(self):
    #     return f"{self.id}"

    def get_absolute_url(self):
        return f"/player/{self.id}"

    def get_verbose_last_match_date(self):
        return unix_to_string(self.last_match_date)

    def get_verbose_first_match_date(self):
        return unix_to_string(self.first_match_date)
