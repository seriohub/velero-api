import subprocess

from fastapi import WebSocketDisconnect

from connection_manager import *
from helpers.json_response import *


@handle_exceptions_async_method
async def send_message(message):
    try:
        print('bash command:', message)
        await manager.broadcast(message)
        pass
    except WebSocketDisconnect:
        print('error')


@handle_exceptions_async_method
async def run_process_check_output(cmd, publish_message=True, cwd= './'):
    try:
        if publish_message:
            await send_message(' '.join(cmd))
        output = subprocess.check_output(
            cmd, stderr=subprocess.PIPE, cwd=cwd).decode('utf-8')
        if output.startswith('An error occurred'):
            return {'error': {'title': 'Error',
                              'description': f"{output} {'.'.join(cmd)}"}
                    }
        return {'data': output}
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode('utf-8').strip()
        err = FailedRequest()
        err.error['title'] = "Error"
        err.error['description'] = f"{error_message}"
        return {'error': err}


@handle_exceptions_async_method
async def run_process_check_call(cmd, publish_message=True):
    try:
        if publish_message:
            await send_message(' '.join(cmd))
        subprocess.check_call(cmd)
        return {'data': 'done'}
    except Exception as e:
        err = FailedRequest()
        err.error.title = "Error"
        err.error.description = f"{str(e)} - {'.'.join(cmd)}"
        return {'error': err}
