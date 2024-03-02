import subprocess

from fastapi import WebSocketDisconnect

from core.config import ConfigHelper
from helpers.connection_manager import manager
from helpers.printer import PrintHelper

config = ConfigHelper()
print_ls = PrintHelper('[bash tracer]',
                       level=config.get_internal_log_level())


async def send_message(message):
    try:
        print_ls.debug(message)
        # print('bash command:', message)
        await manager.broadcast(message)
        pass
    except WebSocketDisconnect:
        print_ls.error('send message error')


async def run_process_check_output(cmd, publish_message=True, cwd='./'):
    try:
        if publish_message:
            await send_message(' '.join(cmd))
        output = subprocess.check_output(
            cmd, stderr=subprocess.PIPE, cwd=cwd).decode('utf-8')
        if output.startswith('An error occurred'):
            print("Error:", output)
            raise Exception('Error')

        return {'success': True, 'data': output}
    except subprocess.CalledProcessError as e:
        # print("Error", e)
        print_ls.error("Error" + str(e))
        error = {'success': False, 'error': {'title': 'Run Process Check Output Error',
                                             'description': ' '.join(str(cmd)) + str(e.stderr.decode('utf-8').strip())
                                             }
                 }
        return error
    except Exception as e:
        # print("Error", e)
        print_ls.error("Error" + str(e))
        error = {'success': False, 'error': {'title': 'Run Process Check Output Error',
                                             'description': str(e)
                                             }
                 }
        return error


async def run_process_check_call(cmd, publish_message=True):
    try:
        if publish_message:
            await send_message(' '.join(cmd))
        subprocess.check_call(cmd)
        return {'success': True}
    except Exception as e:
        error = {'success': False, 'error': {'title': 'Run Process Check Output Error',
                                             'description': ' '.join(str(cmd)) + str(e)
                                             }
                 }
        return error
