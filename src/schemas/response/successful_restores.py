from typing import List
from models.k8s.restore import RestoreResponseSchema
from schemas.response.successful_request import SuccessfulRequest


class SuccessfulRestoreResponse(SuccessfulRequest[List[RestoreResponseSchema]]):
    pass
