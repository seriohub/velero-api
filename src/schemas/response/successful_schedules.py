from typing import List
from models.k8s.schedule import ScheduleResponseSchema
from schemas.response.successful_request import SuccessfulRequest


class SuccessfulScheduleResponse(SuccessfulRequest[List[ScheduleResponseSchema]]):
    pass
