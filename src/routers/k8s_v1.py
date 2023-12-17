from fastapi import APIRouter

from helpers.handle_exceptions import *
from libs.k8s_v1 import K8sV1

router = APIRouter()

k8s = K8sV1()


@router.get('/k8s/ns/get')
@handle_exceptions_async_method
async def k8s_ns_get():
    return k8s.get_ns()


@router.get('/k8s/credential/get')
@handle_exceptions_async_method
async def get_credential(secret_name=None, secret_key=None):
    return await k8s.get_credential(secret_name, secret_key)


@router.get('/k8s/credential/default/get')
@handle_exceptions_async_method
async def get_default_credential():
    return await k8s.get_default_credential()
