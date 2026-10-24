from datetime import date

import pytest
from fastapi import HTTPException

from app.services.reports import attendance_percent, normalized_week, week_summary

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(('attended', 'missed', 'expected'), [
    (0, 0, 0),
    (1, 0, 100),
    (0, 1, 0),
    (2, 1, 66.67),
    (1, 2, 33.33),
])
def test_attendance_percent(attended, missed, expected):
    assert attendance_percent(attended, missed) == expected


def test_planned_is_excluded_from_percentage():
    class FakeResult:
        def all(self):
            return [('planned', 8), ('attended', 1), ('missed', 1)]

    class FakeSession:
        def execute(self, statement):
            return FakeResult()

    result = week_summary(FakeSession(), [15], date(2026, 10, 19))
    assert result['training_count'] == 10
    assert result['attendance_percent'] == 50


def test_week_start_must_be_monday():
    assert normalized_week(date(2026, 10, 19)) == date(2026, 10, 19)
    with pytest.raises(HTTPException) as error:
        normalized_week(date(2026, 10, 20))
    assert error.value.status_code == 422
