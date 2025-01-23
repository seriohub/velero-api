from pydantic import BaseModel

class UpdateBackupExpiration(BaseModel):
    backupName: str
    expiration: str
