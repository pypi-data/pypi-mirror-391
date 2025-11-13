# bl3d --- Domain Driven Design library
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

import re
import sys
from abc import ABC, abstractproperty
from dataclasses import asdict, dataclass
from typing import Any

from bles import Event, EventStore


@dataclass(frozen=True)
class DomainEvent(ABC):
    """An event that happened in the domain."""

    version: int

    @abstractproperty
    def aggregate_id(self) -> str:
        """An identifier that uniquely identifies the aggregate
        that emitted the domain event.
        """
        ...


@dataclass(frozen=True)
class EntityState(ABC):
    """The state of an entity.

    A new state is created by applying an domain event to it.
    """

    class UnknownEvent(Exception):
        pass

    class IncompatibleVersions(Exception):
        pass

    version: int

    def apply(self, event: DomainEvent) -> "EntityState":
        # Could this be `> self.version`?
        if event.version != self.version + 1:
            raise EntityState.IncompatibleVersions(f"{self.version} vs {event.version}")

        event_name = event.__class__.__name__
        method_name = f"apply_{camel_to_snake(event_name)}"
        if method := getattr(self, method_name, None):
            return method(event)  # type: ignore
        raise EntityState.UnknownEvent(event_name)


class History:
    """A sequence of events that happened inside the domain."""

    EVENT_MODULE = sys.modules[__name__]

    class EvenNotHandled(NotImplementedError):
        def __init__(self, name: str) -> None:
            super().__init__(f"History cannot handle event `{name}`!")

    class ReadError(AttributeError):
        def __init__(self, name: str, data: dict[str, Any]) -> None:
            super().__init__(f"Cannot read event's data `{name}`: {data}")

    def __init__(self, event_store: EventStore) -> None:
        self.__store = event_store

    def read(self, stream: str) -> list[DomainEvent]:
        return [self.__event(e) for e in self.__store.for_stream(stream).read()]

    def __event(self, event: Event) -> DomainEvent:
        try:
            class_ = getattr(self.EVENT_MODULE, event.name)
            return class_(  # type: ignore
                **event.data,
                version=event.version,
            )
        except AttributeError:
            raise History.EvenNotHandled(event.name)
        except TypeError:
            raise History.ReadError(event.name, event.data)

    def __lshift__(self, domain_events: list[DomainEvent]) -> None:
        self.__store.record(
            [
                Event(
                    stream_id=e.aggregate_id,
                    version=e.version,
                    name=e.__class__.__name__,
                    data=self.__event_as_dict(e),
                )
                for e in domain_events
            ]
        )

    def __event_as_dict(self, domain_event: DomainEvent) -> dict[str, Any]:
        data = asdict(domain_event)
        del data["version"]
        return data


def camel_to_snake(string: str) -> str:
    # https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", string)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()
