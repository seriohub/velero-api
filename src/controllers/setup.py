import os
from fastapi.responses import JSONResponse

from configs.config_boot import config_app

from schemas.response.successful_request import SuccessfulRequest

from service.k8s import get_config_map_service
from service.setup import get_velero_version_service




async def get_env_handler():
    if os.getenv('K8S_IN_CLUSTER_MODE').lower() == 'true':
        env_data = await get_config_map_service(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                configmap_name='velero-api-config')

    else:
        env_data = config_app.get_env_variables()

    response = SuccessfulRequest(payload=env_data)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def get_velero_version_handler():
    payload = await get_velero_version_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)
