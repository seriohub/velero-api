from typing import List

from models.k8s.bsl import BackupStorageLocationResponseSchema
from schemas.response.successful_request import SuccessfulRequest


class SuccessfulBslResponse(SuccessfulRequest[List[BackupStorageLocationResponseSchema]]):
    pass
