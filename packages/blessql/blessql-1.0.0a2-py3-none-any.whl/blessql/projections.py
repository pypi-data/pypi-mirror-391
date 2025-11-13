# blessql --- Event Sourcing implemented with SQLAlchemy
# Copyright © 2023 Bioneland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from dataclasses import dataclass
from typing import Optional

from bles import Ledger as LedgerInterface
from bles import ProjectorStatuses
from sqlalchemy import Column, Enum, Integer, String, Table, create_engine, select
from sqlalchemy.orm import Session, registry

REGISTRY = registry()


@dataclass
class Record:
    name: str
    status: ProjectorStatuses
    position: int


class Ledger(LedgerInterface):
    def __init__(self, session: Session, autocommit: bool = True) -> None:
        self.__session = session
        self.__autocommit = autocommit

    def __record(self, name: str) -> Record:
        stmt = select(Record).where(Record.name == name)  # type: ignore[arg-type]
        if record := self.__session.scalars(stmt).first():
            return record
        raise Ledger.UnknownProjector(name)

    def status(self) -> list[tuple[str, ProjectorStatuses, int]]:
        stmt = select(Record)
        return [(i.name, i.status, i.position) for i in self.__session.scalars(stmt)]

    def knows(self, name: str) -> bool:
        try:
            _ = self.__record(name)
            return True
        except Exception:
            return False

    def register(self, name: str) -> None:
        if self.knows(name):
            raise Ledger.ProjectorAlreadyRegistered(name)
        self.__session.add(Record(name, ProjectorStatuses.STALLED, 0))
        self.__session.commit() if self.__autocommit else None

    def forget(self, name: str) -> None:
        try:
            self.__session.delete(self.__record(name))
            self.__session.commit() if self.__autocommit else None
        except Ledger.UnknownProjector:
            pass

    def position(self, name: str) -> int:
        return self.__record(name).position

    def update_position(self, name: str, position: int) -> None:
        self.__record(name).position = position
        self.__session.commit() if self.__autocommit else None

    def find(self, status: Optional[ProjectorStatuses] = None) -> list[str]:
        stmt = select(Record)
        if status:
            stmt = stmt.where(Record.status == status)  # type: ignore[arg-type]
        return [r.name for r in self.__session.scalars(stmt)]

    def mark_as(self, name: str, status: ProjectorStatuses) -> None:
        self.__record(name).status = status
        self.__session.commit() if self.__autocommit else None


def initialize(dsn: str) -> None:
    REGISTRY.metadata.create_all(create_engine(dsn))


ledger_records_table = Table(
    "ledger_records",
    REGISTRY.metadata,
    Column("name", String(50), primary_key=True),
    Column("status", Enum(ProjectorStatuses)),
    Column("position", Integer),
)
REGISTRY.map_imperatively(Record, ledger_records_table)
