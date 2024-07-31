from sqlalchemy import Index, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from common.utils import unix_to_datetime, get_delta_time, convert_to_datetime
from config.db import a_id, a_small_int, a_big_int, a_str, a_bool, Base, a_char


class Team(Base):
    __tablename__ = 'teams'

    id: Mapped[a_id]
    name: Mapped[a_str]
    tag: Mapped[a_str]
    date_created: Mapped[a_char]
    is_pro: Mapped[a_bool]
    is_locked: Mapped[a_bool]
    country_code: Mapped[a_str]
    url: Mapped[a_str]
    logo: Mapped[a_str]
    base_logo: Mapped[a_str]
    banner_logo: Mapped[a_str]
    sponsor_logo: Mapped[a_str]
    win_count: Mapped[a_small_int]
    loss_count: Mapped[a_small_int]
    rank: Mapped[a_small_int]
    last_match_date_time: Mapped[a_big_int]
    coach_steam_account_id: Mapped[a_big_int]
    country_name: Mapped[a_str]
    members = relationship("TeamMember", back_populates="team")

    __table_args__ = (
        Index('ix_teams_name', 'name'),
    )

    def __str__(self):
        return f"id-{self.id}-{self.name}"

    def get_absolute_url(self):
        return f"/team/{self.id}"

    def get_verbose_last_match_date_time(self):
        last_match_dt = unix_to_datetime(self.last_match_date_time)
        return get_delta_time(last_match_dt)

    # @property
    # def get_members(self):
    #     return self.members.active().order_by('-last_match_id')


class TeamMember(Base):
    __tablename__ = 'team_members'

    steam_account_id = mapped_column(BigInteger, ForeignKey("steam_accounts.id"))
    team_id = mapped_column(BigInteger, ForeignKey("teams.id"))
    first_match_id: Mapped[a_big_int]
    first_match_date_time: Mapped[a_char]
    last_match_id: Mapped[a_big_int]
    last_match_date_time: Mapped[a_char]
    team = relationship("Team", foreign_keys=[team_id])
    steam_account = relationship("SteamAccount", foreign_keys=[steam_account_id])

    __table_args__ = (
        Index('ix_team_members_team_id', 'team_id'),
        Index('ix_team_members_steam_account_id', 'steam_account_id'),
    )

    def __str__(self):
        name = self.team.name if self.team and self.team.name else f"Team NA {self.team_id}"
        return f"{name}"

    def get_absolute_url(self):
        return f"/player/{self.steam_account_id}"

    def get_verbose_last_match_date_time(self):
        return convert_to_datetime(self.last_match_date_time)

    def get_verbose_first_match_date_time(self):
        return convert_to_datetime(self.first_match_date_time)

    def get_url_first_match(self):
        return f"/match/{self.first_match_id}/"

    def get_url_last_match(self):
        return f"/match/{self.last_match_id}/"
