from fastapi.responses import JSONResponse

from utils.handle_exceptions import handle_exceptions_controller
from core.config import ConfigHelper

from api.common.response_model.successful_request import SuccessfulRequest
from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.message import Message

from service.watchdog_service import WatchdogService
from api.v1.schemas.apprise_test_service import AppriseTestService
from api.v1.schemas.create_user_service import CreateUserService
from api.v1.schemas.delete_user_service import DeleteUserService
from api.v1.schemas.update_user_config import UpdateUserConfig

watchdog = WatchdogService()
config_app = ConfigHelper()

class Watchdog:

    @handle_exceptions_controller
    async def version(self):
        payload = await watchdog.version()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def send_report(self):
        payload = await watchdog.send_report()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def get_env(self):

        payload = await watchdog.get_env_variables()

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def get_cron(self):

        payload = await watchdog.get_cron(job_name=config_app.get_cronjob_name())

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def send_test_notification(self,
                                     provider: AppriseTestService):
        payload = await watchdog.send_test_notification(provider.config)
        if not payload['success']:

            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Send Notification', description=f"Test notification done!", type='Success')
        response = SuccessfulRequest(notifications=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def restart(self):
        payload = await watchdog.restart()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def user_configs(self):
        payload = await watchdog.get_user_configs()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def update_user_configs(self, user_configs: UpdateUserConfig):
        payload = await watchdog.update_user_configs(user_configs)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest()
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def user_services(self):
        payload = await watchdog.get_user_services()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def create_user_services(self, service: CreateUserService):
        payload = await watchdog.create_user_services(service.config)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Watchdog',
                      description=f"New service added!",
                      type='INFO')
        response = SuccessfulRequest(notifications=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=201)

    @handle_exceptions_controller
    async def delete_user_services(self, service: DeleteUserService):
        payload = await watchdog.delete_user_services(service.config)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Watchdog',
                      description=f'Service deleted!',
                      type='INFO')

        response = SuccessfulRequest()
        response.notifications = [msg.toJSON()]
        return JSONResponse(content=response.toJSON(), status_code=200)
