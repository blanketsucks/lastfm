from __future__ import annotations

from typing import Dict, Any, NamedTuple

import datetime

class WeeklyChart(NamedTuple):
    start: datetime.datetime
    end: datetime.datetime

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WeeklyChart:
        return cls(
            start=datetime.datetime.fromtimestamp(int(data['from'])),
            end=datetime.datetime.fromtimestamp(int(data['to']))
        )

