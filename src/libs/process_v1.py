import subprocess

from fastapi import WebSocketDisconnect

from app_settings import *


@handle_exceptions_async_method
async def send_message(message):
    try:
        print("bash command:", message)
        await manager.broadcast(message)
        pass
    except WebSocketDisconnect:
        print("error")


@handle_exceptions_async_method
async def run_process_check_output(cmd, publish_message=True):
    try:
        if publish_message:
            await send_message(' '.join(cmd))
        output = subprocess.check_output(
            cmd, stderr=subprocess.PIPE).decode("utf-8")
        if output.startswith("An error occurred"):
            return {'error': {'title': 'Error',
                              'description': f"{output} {'.'.join(cmd)}"}
                    }
        return {'data': output}
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode("utf-8").strip()
        return {'error': {'title': 'Error',
                          'description': error_message}
                }


@handle_exceptions_async_method
async def run_process_check_call(cmd, publish_message=True):
    try:
        print(cmd)
        if publish_message:
            await send_message(' '.join(cmd))
        subprocess.check_call(cmd)
        return {'data': 'done'}
    except Exception as e:
        return {'error': {'title': 'Error',
                          'description': f"{str(e)} - {'.'.join(cmd)}"}
                }
