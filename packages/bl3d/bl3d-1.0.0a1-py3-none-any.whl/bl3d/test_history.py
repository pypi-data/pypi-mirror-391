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

import sys
from dataclasses import dataclass

from .event_sourcing import DomainEvent, History


@dataclass(frozen=True)
class SomethingHasHappened(DomainEvent):
    my_aggregate_id: str
    my_data: str

    @property
    def aggregate_id(self) -> str:
        return self.my_aggregate_id


class TestHistory(History):
    EVENT_MODULE = sys.modules[__name__]
