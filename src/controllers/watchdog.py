from fastapi.responses import JSONResponse

from configs.config_boot import config_app

from schemas.response.successful_request import SuccessfulRequest
from schemas.notification import Notification
from schemas.request.apprise_test_service import AppriseTestServiceRequestSchema
from schemas.request.create_user_service import CreateUserServiceRequestSchema
from schemas.request.update_user_config import UpdateUserConfigRequestSchema

from service.watchdog import (get_watchdog_version_service,
                              send_watchdog_report,
                              get_watchdog_env_services,
                              get_watchdog_report_cron_service,
                              send_watchdog_test_notification_service,
                              restart_watchdog_service,
                              get_watchdog_user_configs_service,
                              update_watchdog_user_configs_service,
                              get_apprise_services,
                              create_apparise_services,
                              delete_apprise_services)


async def version_handler():
    payload = await get_watchdog_version_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def send_report_handler():
    payload = await send_watchdog_report()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def get_env_handler():
    payload = await get_watchdog_env_services()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def get_cron_handler():
    payload = await get_watchdog_report_cron_service(job_name=config_app.watchdog.report_cronjob_name)

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def send_test_notification_handler(provider: AppriseTestServiceRequestSchema):
    print("---", provider.config)
    payload = await send_watchdog_test_notification_service(provider.config)

    msg = Notification(title='Send Notification', description=f"Test notification done!", type_='Success')
    response = SuccessfulRequest(notifications=[msg], payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def restart_handler():
    payload = await restart_watchdog_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def user_configs_handler():
    payload = await get_watchdog_user_configs_service()
    secrets = await get_apprise_services()

    payload['APPRISE'] = ';'.join(secrets)
    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def update_user_configs_handler(user_configs: UpdateUserConfigRequestSchema):
    payload = await update_watchdog_user_configs_service(user_configs)

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def get_apprise_services_handler():
    payload = await get_apprise_services()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def create_apprise_service_handler(service: CreateUserServiceRequestSchema):
    payload = await create_apparise_services(service.config)

    msg = Notification(title='Watchdog',
                       description=f"New service added!",
                       type_='INFO')
    response = SuccessfulRequest(notifications=[msg], payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=201)


async def delete_apprise_service_handler(service: str):
    payload = await delete_apprise_services(service)

    msg = Notification(title='Watchdog',
                       description=f'Service deleted!',
                       type_='INFO')

    response = SuccessfulRequest(payload=payload)
    response.notifications = [msg]
    return JSONResponse(content=response.model_dump(), status_code=200)
