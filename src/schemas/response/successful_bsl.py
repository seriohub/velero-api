from typing import List

from models.k8s.bsl import BackupStorageLocationResponseSchema
from vui_common.schemas.response.successful_request import SuccessfulRequest


class SuccessfulBslResponse(SuccessfulRequest[List[BackupStorageLocationResponseSchema]]):
    pass
