from typing import Any, Dict, List, TypeVar, Generic, Union
from pydantic import BaseModel, Field
from schemas.notification import Notification
from schemas.message import Message

T = TypeVar("T")  # generic type definition for the payload


class SuccessfulRequest(BaseModel, Generic[T]):
    status: str = "success"
    data: Union[T, Dict[str, Any], List[Any]] = Field(default_factory=dict)
    notifications: List[Notification] = Field(default_factory=list)
    messages: List[Message] = Field(default_factory=list)

    def __init__(self, payload: Union[T, List[T], Dict[str, Any], None] = None,
                 # metadata: Dict[str, Any] = None,
                 notifications: List[Union[Notification, Dict[str, Any]]] = None,
                 messages: List[Union[Message, Dict[str, Any]]] = None, **data: Any):
        formatted_data = payload
        super().__init__(
            data=formatted_data,
            notifications=[Notification(**n) if isinstance(n, dict) else n for n in (notifications or [])],
            messages=[Message(**m) if isinstance(m, dict) else m for m in (messages or [])]
        )

    def model_dump(self, exclude_unset=True, **kwargs):
        """Automatically remove empty fields before serialization"""
        base_dict = super().model_dump(exclude_unset=exclude_unset, **kwargs)

        # ✅ Rimuove i campi se vuoti
        # if not base_dict.get("data"):
        #     base_dict.pop("data", None)
        if not base_dict.get("notifications"):
            base_dict.pop("notifications", None)
        if not base_dict.get("messages"):
            base_dict.pop("messages", None)

        return base_dict
