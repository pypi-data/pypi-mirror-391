"""
Search Terms
"""
from __future__ import annotations

import datetime

from dataclasses import dataclass
from collections.abc import Sequence  # noqa: TC003


@dataclass(eq=True, frozen=True)
class SearchTerms:  # pylint: disable=too-many-instance-attributes
    """
    dataclass containing all search fields.
    """
    def __post_init__(self) -> None:
        if self.patid is not None:
            assert isinstance(self.patid, str)
            # assert len(self.patid) == 7

    date_range: datetime.date | tuple[datetime.date, datetime.date] | None = None
    timestamp: str | None = None
    study_desc: str | None = None
    study_uid: str | None = None
    patid: str | None = None
    pat_name: str | None = None
    accession_number: str | None = None
    modalities: Sequence[str] | None = None


def get_date_query(date_range: datetime.date | tuple[datetime.date, datetime.date] | None) -> str:
    """ Convert one of two datetime.date objects to a DICOM compatible date range."""
    if date_range is None:
        return '""'

    if isinstance(date_range, tuple):
        try:
            begin_date = date_range[0].strftime('%Y%m%d')
            end_date = date_range[1].strftime('%Y%m%d')
        except ValueError:
            return '""'

        return f'{begin_date}-{end_date}'

    if isinstance(date_range, datetime.date):
        try:
            return date_range.strftime('%Y%m%d')
        except ValueError:
            return '""'

    return '""'
