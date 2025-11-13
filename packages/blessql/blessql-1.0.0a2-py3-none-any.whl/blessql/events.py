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

from datetime import datetime, timezone
from time import sleep
from typing import Iterator, Optional

from bles import Event
from bles import EventStore as EventStoreInterface
from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Integer,
    String,
    Table,
    UniqueConstraint,
    create_engine,
    select,
)
from sqlalchemy.orm import Session, registry
from sqlalchemy.sql.expression import Select

REGISTRY = registry()


class EventStore(EventStoreInterface):
    SLEEP_DURATION = 0.1

    def __init__(self, session: Session) -> None:
        self.__session = session
        self.__stream_id = ""

    def record(self, events: list[Event]) -> None:
        """Records a series of events.

        `records` does not reset `position` nor `recorded_at` to make it possible
        to clone stores, but it will set `recorded_at` to the current date-time
        if it is not provided.
        """
        for e in events:
            if not e.recorded_at:
                e.recorded_at = datetime.now(timezone.utc)
            self.__session.add(e)

    def for_stream(self, name: str) -> "EventStore":
        event_store = EventStore(self.__session)
        event_store.__stream_id = name
        return event_store

    def read(self, start: int = 0, follow: bool = False) -> Iterator[Event]:
        while True:
            for e in self.__read_events(start):
                yield e
            if not follow:
                break
            sleep(self.SLEEP_DURATION)

    def __read_events(self, start: int = 0) -> Iterator[Event]:
        stmt = self.__select_events()
        if start:
            stmt = stmt.filter(events_table.c.position >= start)
        stmt = stmt.order_by(events_table.c.position.asc())
        for e in self.__session.scalars(stmt):
            yield e

    def __select_events(self) -> Select[tuple[Event]]:
        stmt = select(Event)
        if self.__stream_id and self.__stream_id != "*":
            stmt = stmt.where(
                Event.stream_id == self.__stream_id  # type: ignore[arg-type]
            )
        return stmt

    def last(self) -> Optional[Event]:
        stmt = self.__select_events().order_by(events_table.c.position.desc()).limit(1)
        return self.__session.scalars(stmt).first()


def initialize(dsn: str) -> None:
    REGISTRY.metadata.create_all(create_engine(dsn))


events_table = Table(
    "events",
    REGISTRY.metadata,
    Column("position", Integer, primary_key=True),
    Column("stream_id", String(36)),
    Column("version", Integer),
    Column("name", String(99)),
    Column("data", JSON),
    Column("recorded_at", DateTime),
    UniqueConstraint("stream_id", "version", name="stream_version"),
)
REGISTRY.map_imperatively(Event, events_table)
