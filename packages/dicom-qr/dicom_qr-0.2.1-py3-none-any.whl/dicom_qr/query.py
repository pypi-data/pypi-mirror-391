from __future__ import annotations

import typing
from typing import Protocol, Self

from loguru import logger

from dicom_qr.dicom_web.qido_rs import QueryPacsRS
from dicom_qr.dimse.query_c_find import QueryPacsFind

if typing.TYPE_CHECKING:
    from collections import defaultdict
    from collections.abc import Sequence
    from pydicom.uid import UID

    from dicom_qr.database import SeriesData, StudyData
    from dicom_qr.search import SearchTerms
    from dicom_qr.settings import PacsConfig


class QueryPacs(Protocol):
    """ Protocol describing RetrievePacs. """

    def get_studies(self, search_terms: SearchTerms) -> list[StudyData]:
        """Get the studies matching the search_terms."""

    def get_series_for_study(self, study_uid: str | UID, modalities: Sequence[str] | None = None) -> list[SeriesData]:
        """Get the series for 'study_uid', filtered by modalities (if specified)."""

    def get_modalities_for_accession_number(self, search_terms: SearchTerms) -> set[str]:
        """ Get modalities for matching the 'accession_number' in the search_terms."""

    def get_studies_for_patient(self, search_terms: SearchTerms) -> defaultdict[str, list[StudyData]]:
        """ Get all studies matching the 'pat_name' in the search_terms."""

    def __enter__(self) -> Self:
        ...

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        ...


def get_query(pacs_config: PacsConfig) -> QueryPacs:
    """ factory method to create QueryPacs based on the *dicomweb_url* specified in *pacs_config*."""
    if pacs_config.dicom_web is not None:
        logger.trace(f"Using DICOMWeb URL: {pacs_config.dicom_web.url}")
        return QueryPacsRS(pacs_config=pacs_config)

    if pacs_config.dimse is not None:
        logger.trace(f"Using DICOM C_FIND: {pacs_config.dimse.server_ae_ip}")
        return QueryPacsFind(pacs_config=pacs_config)

    raise RuntimeError('Both DICOM Web and DIMSE settings are empty')
