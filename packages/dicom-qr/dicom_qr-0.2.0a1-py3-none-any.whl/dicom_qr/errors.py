from pydicom import Dataset


class QueryError(Exception):
    """Query exception"""

    def __init__(self, response: Dataset) -> None:
        super().__init__('Error perfoming query')
        self.response = response
