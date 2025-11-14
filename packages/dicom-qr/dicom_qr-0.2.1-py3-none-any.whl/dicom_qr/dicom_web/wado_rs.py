import string
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Self

import pydicom
from requests.auth import HTTPBasicAuth
from dicomweb_client.api import DICOMwebClient
from dicomweb_client.session_utils import create_session_from_auth

from dicom_qr.database import SeriesData
from dicom_qr.retrieve_utils import DicomStatus, RetrieveResult
from dicom_qr.scp import Anonymizer, dataset_to_filename_template_dict, dummy_anonymize, get_prefix
from dicom_qr.settings import PacsConfig


def _handle_store(dataset: pydicom.Dataset,
                  base_folder: Path,
                  folder_template: str,
                  anonimyzer: Anonymizer,
                  uid_mapping: Callable[[str], str],
                  folder_callback: Callable[[Path], None],
                  sop_class_uid: Iterable[str] | None) -> RetrieveResult:
    dataset = anonimyzer(dataset)

    try:
        ds_dict = dataset_to_filename_template_dict(dataset)

        if sop_class_uid is not None and 'SOPClassUID' in ds_dict and ds_dict['SOPClassUID'] not in sop_class_uid:
            return RetrieveResult(status=DicomStatus.DATASET_DOESNT_MATCH_SOP_CLASS)

        if 'FolderUID' in folder_template:
            try:
                ds_dict['FolderUID'] = uid_mapping(ds_dict['SeriesInstanceUID'])
            except KeyError:
                ds_dict['FolderUID'] = 'NA'

        folder_name = base_folder / string.Template(folder_template).substitute(ds_dict)
        folder_name.mkdir(parents=True, exist_ok=True)
        folder_callback(folder_name)

        filename = Path(get_prefix(dataset) + dataset.SOPInstanceUID + '.dcm')

        dataset.save_as(folder_name / filename, write_like_original=False)
    except TypeError:
        return RetrieveResult(status=DicomStatus.CANCEL)

    return RetrieveResult(status=DicomStatus.SUCCESS)


class RetrievePacsWado:
    def __init__(self, pacs_config: PacsConfig,
                 uid_mapping: Callable[[str], str],
                 folder_callback: Callable[[Path], None],
                 anonymizer: Anonymizer = dummy_anonymize,
                 sop_class_uid: Iterable[str] | None = None) -> None:
        self.pacs_config = pacs_config
        self.anonymizer = anonymizer
        self.uid_mapping = uid_mapping
        self.folder_callback = folder_callback
        self.sop_class_uid = sop_class_uid

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

    def retrieve_images_for_a_series(self, series_data: SeriesData) -> RetrieveResult | None:
        instances = self.client.retrieve_series(
            study_instance_uid=series_data.StudyInstanceUID,
            series_instance_uid=series_data.SeriesInstanceUID,
            media_types=(("application/dicom", "*"), )
        )
        for instance in instances:
            _handle_store(
                dataset=instance,
                base_folder=self.pacs_config.base_folder,
                folder_template=self.pacs_config.folder_template,
                anonimyzer=self.anonymizer,
                folder_callback=self.folder_callback,
                sop_class_uid=self.sop_class_uid,
                uid_mapping=self.uid_mapping
            )
        return RetrieveResult(status=DicomStatus.SUCCESS, completed=len(instances))

    def retrieve(self, dataset: pydicom.Dataset) -> RetrieveResult | None:
        raise NotImplementedError
