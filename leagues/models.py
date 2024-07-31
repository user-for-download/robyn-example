from sqlalchemy import ForeignKey, BigInteger, Index
from sqlalchemy.orm import Mapped, relationship, mapped_column

from common.utils import date_as_number, unix_to_datetime, get_delta_time, unix_to_string
from config.db import a_id, a_str, a_text, a_bool, a_small_int, a_big_int, Base


# class LeagueQuery(Session):
#     def tier2(self):
#         return self.query(League).filter(
#             League.tier >= 2
#         ).filter(
#             League.id >= 16000
#         ).filter(
#             League.is_over.is_(False)
#         ).order_by(League.id.desc())
#
#     def need_to_update(self):
#         return self.query(League).filter(
#             League.tier >= 2
#         ).filter(
#             League.is_over.is_(False)
#         )
#
#     def update_is_over(self):
#         now = date_as_number()
#         self.query(League).filter(
#             League.end_datetime < now,
#             League.is_over.is_(False)
#         ).update({League.is_over: True})


class League(Base):
    __tablename__ = 'leagues'

    id: Mapped[a_id]
    registration_period: Mapped[a_small_int]
    country: Mapped[a_str]
    venue: Mapped[a_str]
    private: Mapped[a_bool]
    city: Mapped[a_str]
    description: Mapped[a_text]
    has_live_matches: Mapped[a_bool]
    tier: Mapped[a_small_int]
    tournament_url: Mapped[a_text]
    free_to_spectate: Mapped[a_bool]
    is_followed: Mapped[a_bool]
    last_match_date: Mapped[a_big_int]
    pro_circuit_points: Mapped[a_small_int]
    banner: Mapped[a_str]
    stop_sales_time: Mapped[a_str]
    image_uri: Mapped[a_text]
    display_name: Mapped[a_str]
    end_datetime: Mapped[a_big_int]
    name: Mapped[a_str]
    prize_pool: Mapped[a_big_int]
    base_prize_pool: Mapped[a_big_int]
    region: Mapped[a_small_int]
    start_datetime: Mapped[a_big_int]
    status: Mapped[a_small_int]
    is_over: Mapped[a_bool]
    series = relationship("Series", back_populates="league")

    __table_args__ = (
        Index('ix_leagues_name', 'name'),
        Index('ix_leagues_is_over', 'is_over'),
    )

    def __str__(self):
        return f"lg{self.id} name-{self.display_name}"

    def delete(self, session):
        for series in self.series:
            series.delete(session)
        super().delete(session)

    def restore(self, session):
        for series in self.series:
            series.deleted_at = None
        self.deleted_at = None
        self.save(session)

    def get_absolute_url(self):
        return f"/league/{self.id}"

    def get_verbose_start_datetime(self):
        return unix_to_string(self.start_datetime)

    def get_verbose_end_datetime(self):
        return unix_to_string(self.end_datetime)

    def has_started(self) -> bool:
        return self.start_datetime >= date_as_number()


class Series(Base):
    __tablename__ = 'series'

    id: Mapped[a_id]
    type: Mapped[a_small_int]
    team_one_win_count: Mapped[a_small_int]
    team_two_win_count: Mapped[a_small_int]
    winning_team_id: Mapped[a_big_int]
    last_match_date_time: Mapped[a_big_int]
    losing_team_id: Mapped[a_big_int]
    is_over: Mapped[a_bool]

    league_id = mapped_column(BigInteger, ForeignKey("leagues.id"))
    team_one_id = mapped_column(BigInteger, ForeignKey("teams.id"))
    team_two_id = mapped_column(BigInteger, ForeignKey("teams.id"))

    team_one = relationship("Team", foreign_keys=[team_one_id])
    team_two = relationship("Team", foreign_keys=[team_two_id])
    league = relationship("League", foreign_keys=[league_id])
    matches = relationship("Match", back_populates="series")

    __table_args__ = (
        Index('ix_series_league_id', 'league_id'),
        Index('ix_series_team_one_id', 'team_one_id'),
        Index('ix_series_team_two_id', 'team_two_id'),
        Index('ix_series_is_over', 'is_over'),
    )

    def __str__(self):
        return f"lg{self.league_id}/s{self.id}-win-{self.winning_team_id}"

    def get_absolute_url(self):
        return f"/league/{self.league_id}/series/{self.id}/"

    def get_verbose_last_match_date_time(self):
        last_match_dt = unix_to_datetime(self.last_match_date_time)
        return get_delta_time(last_match_dt)

    def get_bo_format_name(self):
        match self.type:
            case 1:
                bo = 3
            case 2:
                bo = 5
            case 3:
                bo = 2
            case _:
                bo = 1
        return bo

    def get_title_team_one(self):
        team_one_name = self.team_one.name if self.team_one and self.team_one.name else f"Team {self.team_one.id}"
        if self.winning_team_id == self.team_one.id:
            return f'<span class="badge text-bg-success">{team_one_name}</span>'
        return team_one_name

    def get_title_team_two(self):
        team_two_name = self.team_two.name if self.team_two and self.team_two.name else f"Team {self.team_two.id}"
        if self.winning_team_id == self.team_two.id:
            return f'<span class="badge text-bg-success">{team_two_name}</span>'
        return team_two_name
