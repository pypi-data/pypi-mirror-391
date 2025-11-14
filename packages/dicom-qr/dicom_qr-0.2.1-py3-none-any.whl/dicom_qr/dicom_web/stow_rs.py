from pathlib import Path
from typing import Self
from collections.abc import Sequence

import pydicom
from pydicom import Dataset
from requests.auth import HTTPBasicAuth
from dicomweb_client.api import DICOMwebClient
from dicomweb_client.session_utils import create_session_from_auth


from dicom_qr.settings import PacsConfig


class StorePacsStow:
    """ Store images in PACS. Using DICOMWeb STOW-RS """

    def __init__(self, pacs_config: PacsConfig) -> None:
        self.pacs_config = pacs_config

        if self.pacs_config.dicom_web is None:
            raise RuntimeError('DicomWeb not set')

        session = None
        if self.pacs_config.dicom_web.username is not None and self.pacs_config.dicom_web.password is not None:
            auth = HTTPBasicAuth(self.pacs_config.dicom_web.username, self.pacs_config.dicom_web.password)
            session = create_session_from_auth(auth)

        self.client = DICOMwebClient(self.pacs_config.dicom_web.url, session=session)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        ...

    def store(self, datasets: Sequence[Path] | Sequence[Dataset]) -> Dataset:
        """
        Store a dataset in PACS.
        :param datasets: datasets to store
        :return: Information about status of stored instances
        """
        if all(isinstance(n, Dataset) for n in datasets):
            return self.client.store_instances(datasets)  # type: ignore

        if all(isinstance(n, Path) for n in datasets):
            return self.client.store_instances([pydicom.dcmread(x) for x in datasets])

        raise NotImplementedError
