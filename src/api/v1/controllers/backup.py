from fastapi.responses import JSONResponse

from utils.handle_exceptions import handle_exceptions_controller
from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest
from api.common.response_model.message import Message

from service.backup_service import BackupService


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
    async def delete(self, backup_name):
        if not backup_name:
            failed_response = FailedRequest(title="Error",
                                            description="Backup name is required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await backupService.delete(backup_name=backup_name)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Delete backup',
                      description=f'Backup {backup_name} deleted request done!',
                      type='INFO')

        response = SuccessfulRequest()
        response.messages = [msg.toJSON()]
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def create(self, info):
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
        response = SuccessfulRequest(messages=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=201)

    @handle_exceptions_controller
    async def create_from_schedule(self, info):

        if not info['scheduleName'] or info['scheduleName'] == '':
            return {'error': {'title': 'Error',
                              'description': 'Schedule name name is required'
                              }
                    }
        payload = await backupService.create_from_schedule(info=info)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Create backup from schedule',
                      description=f"Backup created!",
                      type='INFO')
        response = SuccessfulRequest(messages=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=201)

    @handle_exceptions_controller
    async def update_expiration(self, backup_name, expiration):
        if not backup_name or not expiration:
            failed_response = FailedRequest(title="Error",
                                            description="Backup name and expiration are required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        if not backupService.check_expiration(expiration):
            failed_response = FailedRequest(title="Error",
                                            description="Check expiration format")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await backupService.update_expiration(backup_name=backup_name, expiration=expiration)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='TTL Updated',
                      description=f"Backup {backup_name} expiration updated!",
                      type='INFO')
        response = SuccessfulRequest(messages=[msg.toJSON()])
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
