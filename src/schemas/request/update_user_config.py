from pydantic import BaseModel, field_validator


class UpdateUserConfigRequestSchema(BaseModel):
    backupEnabled: bool
    scheduleEnabled: bool
    notificationSkipCompleted: bool
    notificationSkipDeleting: bool
    notificationSkipInProgress: bool
    notificationSkipRemoved: bool
    processCycleSeconds: int
    expireDaysWarning: int
    reportBackupItemPrefix: str
    reportScheduleItemPrefix: str

    @field_validator(
        "backupEnabled", "scheduleEnabled", "notificationSkipCompleted",
        "notificationSkipDeleting", "notificationSkipInProgress", "notificationSkipRemoved", mode="before"
    )
    @classmethod
    def normalize_bool(cls, value):
        if isinstance(value, str):
            lower_value = value.lower()
            if lower_value == "true":
                return True
            elif lower_value == "false":
                return False
        return value
