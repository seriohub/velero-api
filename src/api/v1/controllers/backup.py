from fastapi.responses import JSONResponse

from utils.handle_exceptions import handle_exceptions_controller
from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest
from api.common.response_model.message import Message

from service.backup_service import BackupService

from api.v1.schemas.create_backup import CreateBackup
from api.v1.schemas.create_backup_from_schedule import CreateBackupFromSchedule
from api.v1.schemas.update_backup_expiration import UpdateBackupExpiration
from api.v1.schemas.delete_backup import DeleteBackup

backupService = BackupService()


class Backup:

    @handle_exceptions_controller
    async def get_settings_create(self):
        payload = await backupService.get_settings_create()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def get(self, schedule_name=None, only_last_for_schedule=False, in_progress=False,
                  publish_message=True):
        payload = await backupService.get(schedule_name=schedule_name,
                                          only_last_for_schedule=only_last_for_schedule,
                                          in_progress=in_progress,
                                          publish_message=publish_message)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def logs(self, backup_name):
        if not backup_name:
            failed_response = FailedRequest(title="Error",
                                            description="Backup name is required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await backupService.logs(backup_name=backup_name)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def describe(self, backup_name):
        if not backup_name:
            failed_response = FailedRequest(title="Error",
                                            description="Backup name is required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await backupService.describe(backup_name=backup_name)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def delete(self, delete_backup: DeleteBackup):
        if not delete_backup.resourceName:
            failed_response = FailedRequest(title="Error",
                                            description="Backup name is required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await backupService.delete(backup_name=delete_backup.resourceName)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Delete backup',
                      description=f'Backup {delete_backup.resourceName} deleted request done!',
                      type='INFO')

        response = SuccessfulRequest()
        response.notifications = [msg.toJSON()]
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def create(self, info: CreateBackup):
        if not info.name or info.name == '':
            failed_response = FailedRequest(title="Error",
                                            description="Backup name is required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await backupService.create(info=info)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Create backup',
                      description=f"Backup {info.name} created!",
                      type='INFO')
        response = SuccessfulRequest(notifications=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=201)

    @handle_exceptions_controller
    async def create_from_schedule(self, create_backup_from_schedule: CreateBackupFromSchedule):

        if not create_backup_from_schedule.scheduleName or create_backup_from_schedule.scheduleName == '':
            return {'error': {'title': 'Error',
                              'description': 'Schedule name name is required'
                              }
                    }
        payload = await backupService.create_from_schedule(schedule_name=create_backup_from_schedule.scheduleName)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Create backup from schedule',
                      description=f"Backup created!",
                      type='INFO')
        response = SuccessfulRequest(notifications=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=201)

    @handle_exceptions_controller
    async def update_expiration(self, update_expiration: UpdateBackupExpiration):
        if not update_expiration.backupName or not update_expiration.expiration:
            failed_response = FailedRequest(title="Error",
                                            description="Backup name and expiration are required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        if not await backupService.check_expiration(update_expiration.expiration):
            failed_response = FailedRequest(title="Error",
                                            description="Check expiration format")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await backupService.update_expiration(backup_name=update_expiration.backupName, expiration=update_expiration.expiration)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='TTL Updated',
                      description=f"Backup {update_expiration.backupName} expiration updated!",
                      type='INFO')
        response = SuccessfulRequest(notifications=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=201)

    @handle_exceptions_controller
    async def get_expiration(self, backup_name):
        if not backup_name:
            failed_response = FailedRequest(title="Error",
                                            description="Backup name is required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await backupService.get_expiration(backup_name=backup_name)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def get_backup_storage_classes(self, backup_name):
        if not backup_name:
            failed_response = FailedRequest(title="Error",
                                            description="Backup name is required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await backupService.get_backup_storage_classes(backup_name=backup_name)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    # async def get_manifest(self, backup_name=None):
    #     payload = await backupService.get_manifest(backup_name)
    #
    #     if not payload['success']:
    #         response = FailedRequest(**payload['error'])
    #         return JSONResponse(content=response.toJSON(), status_code=400)
    #
    #     response = SuccessfulRequest(payload=payload['data'])
    #     return JSONResponse(content=response.toJSON(), status_code=200)
