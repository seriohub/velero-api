from typing import List
from models.k8s.backup import BackupResponseSchema
from vui_common.schemas.response.successful_request import SuccessfulRequest


class SuccessfulBackupResponse(SuccessfulRequest[List[BackupResponseSchema]]):
    pass
