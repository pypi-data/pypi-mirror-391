from collections import defaultdict
from collections.abc import Sequence
from typing import Final, Self

from dicomweb_client.api import DICOMwebClient
from dicomweb_client.session_utils import create_session_from_auth
from pydicom import Dataset
from pydicom.uid import UID
from requests.auth import HTTPBasicAuth

from dicom_qr.database import SeriesData, StudyData
from dicom_qr.search import SearchTerms, get_date_query
from dicom_qr.settings import PacsConfig

STUDY_FIELDS: Final[list[str]] = [
    'StudyInstanceUID',
    'StudyDescription',
    'PatientID',
    'PatientName',
    'PatientBirthDate',
    'StudyID',
    'StudyDate',
    'StudyTime',
    'AccessionNumber',
    'BodyPartExamined',
    'ModalitiesInStudy',
]
SERIES_FIELDS: Final[list[str]] = [
    'StudyInstanceUID',
    'SeriesInstanceUID',
    'Modality',
    'SeriesNumber',
    'ProtocolName',
    'SeriesDescription'
]


def _search_filters(search_terms: SearchTerms) -> dict[str, str]:
    search_filters = {}
    if search_terms.pat_name:
        search_filters['PatientName'] = search_terms.pat_name
    if search_terms.patid:
        search_filters['PatientID'] = search_terms.patid
    if search_terms.accession_number:
        search_filters['AccessionNumber'] = search_terms.accession_number
    if search_terms.study_uid:
        search_filters['StudyInstanceUID'] = search_terms.study_uid
    if search_terms.study_desc:
        search_filters['StudyDescription'] = search_terms.study_desc
    if search_terms.date_range:
        search_filters['StudyDate'] = get_date_query(search_terms.date_range)

    return search_filters


class QueryPacsRS:
    def __init__(self, pacs_config: PacsConfig) -> None:
        self.pacs_config = pacs_config
        if self.pacs_config.dicom_web is None:
            raise RuntimeError('DicomWeb URL not set')

        session = None
        if self.pacs_config.dicom_web.username is not None and self.pacs_config.dicom_web.password is not None:
            auth = HTTPBasicAuth(self.pacs_config.dicom_web.username, self.pacs_config.dicom_web.password)
            session = create_session_from_auth(auth)

        self.client = DICOMwebClient(self.pacs_config.dicom_web.url, session=session)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        pass

    def get_studies(self, search_terms: SearchTerms) -> list[StudyData]:
        def _convert_dataset_to_study_data(ds: Dataset) -> StudyData:
            return StudyData(
                StudyInstanceUID=ds.StudyInstanceUID if 'StudyInstanceUID' in ds else 'NA',
                StudyDescription=ds.StudyDescription if 'StudyDescription' in ds else 'NA',
                PatientID=ds.PatientID if 'PatientID' in ds else 'NA',
                PatientName=ds.PatientName.alphabetic if 'PatientName' in ds else 'NA',
                PatientBirthDate=ds.PatientBirthDate if 'PatientBirthDate' in ds else 'NA',
                StudyID=ds.StudyID if 'StudyID' in ds else 'NA',
                StudyDate=ds.StudyDate if 'StudyDate' in ds else 'NA',
                StudyTime=ds.StudyTime if 'StudyTime' in ds else 'NA',
                AccessionNumber=ds.AccessionNumber if 'AccessionNumber' in ds else 'NA',
                BodyPartExamined=ds.StudyDescription if 'StudyDescription' in ds else 'NA',
                ModalitiesInStudy=ds.ModalitiesInStudy if 'ModalitiesInStudy' in ds else [])

        results = self.client.search_for_studies(search_filters=_search_filters(search_terms), fields=STUDY_FIELDS)
        datasets = [Dataset.from_json(ds) for ds in results]

        return [_convert_dataset_to_study_data(ds) for ds in datasets]

    def get_series_for_study(self, study_uid: str | UID, modalities: Sequence[str] | None = None) -> list[SeriesData]:
        def _convert_dataset_to_series_data(ds: Dataset) -> SeriesData:
            return SeriesData(StudyInstanceUID=ds.StudyInstanceUID if 'StudyInstanceUID' in ds else 'NA',
                              SeriesInstanceUID=ds.SeriesInstanceUID if 'SeriesInstanceUID' in ds else 'NA',
                              Modality=ds.Modality if 'Modality' in ds else 'NA',
                              SeriesNumber=ds.SeriesNumber if 'SeriesNumber' in ds else -1,
                              ProtocolName=ds.ProtocolName if 'ProtocolName' in ds else 'NA',
                              SeriesDescription=ds.SeriesDescription if 'SeriesDescription' in ds else 'NA')

        if modalities is None:
            modalities = []

        results = self.client.search_for_series(
            study_instance_uid=study_uid,
            search_filters={'Modality': ','.join(modalities)},
            fields=SERIES_FIELDS
        )
        datasets = [Dataset.from_json(ds) for ds in results]
        return [_convert_dataset_to_series_data(ds) for ds in datasets]

    def get_modalities_for_accession_number(self, search_terms: SearchTerms) -> set[str]:
        """ Get modalities for matching the 'accession_number' in the search_terms."""
        studies = self.get_studies(search_terms)

        modalities: set[str] = set()
        for study in studies:
            modalities = modalities | set(study.ModalitiesInStudy)

        return modalities

    def get_studies_for_patient(self, search_terms: SearchTerms) -> defaultdict[str, list[StudyData]]:
        """Get the series for 'study_uid', filtered by modalities (if specified)."""
        studies = self.get_studies(search_terms)

        patient_data: defaultdict[str, list[StudyData]] = defaultdict(list)
        for study_data in studies:
            assert study_data.PatientName is not None
            patient_data[study_data.PatientName].append(study_data)

        if search_terms.modalities is None or len(search_terms.modalities) == 0:
            return patient_data

        for pat_data in patient_data.values():
            for study in pat_data:
                study.series = self.get_series_for_study(study.StudyInstanceUID, modalities=search_terms.modalities)

        return patient_data
