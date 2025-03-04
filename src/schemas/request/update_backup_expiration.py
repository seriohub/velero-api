from pydantic import BaseModel, Field

class UpdateBackupExpirationRequestSchema(BaseModel):
    backupName: str
    expiration: str = Field(
        ...,
        pattern=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$',
        description="Expiration date must follow the format YYYY-MM-DDTHH:MM:SSZ"
    )
