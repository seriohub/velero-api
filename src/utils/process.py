import subprocess
import asyncio
from fastapi import WebSocketDisconnect

from core.config import ConfigHelper
from core.context import current_user_var
from helpers.connection_manager import manager
from helpers.printer import PrintHelper

config = ConfigHelper()
print_ls = PrintHelper('[bash tracer]',
                       level=config.get_internal_log_level())


async def send_message(message):
    try:
        print_ls.debug(message)
        # await manager.broadcast(message)
        user = None
        try:
            user = current_user_var.get()
        except:
            print("get failed")
        finally:
            if user is not None:
                await manager.send_personal_message(str(user.id), message)

    except WebSocketDisconnect:
        print_ls.error('send message error')


async def run_process_check_output(cmd, publish_message=True, cwd='./'):
    try:
        if publish_message:
            await send_message('check output: ' + ' '.join(cmd))
        # sync
        # output = subprocess.check_output(
        #     cmd, stderr=subprocess.PIPE, cwd=cwd).decode('utf-8')

        # Starts the secondary process asynchronously
        process = await asyncio.create_subprocess_exec(*cmd,
                                                       stdout=asyncio.subprocess.PIPE,
                                                       stderr=asyncio.subprocess.STDOUT,
                                                       cwd=cwd)

        # Wait for the process to complete and capture the output
        stdout, stderr = await process.communicate()

        # Check for errors in the output
        if stderr:
            # example: await publish_message_function(stderr.decode())
            pass

        # Decode the output and return a string
        output = stdout.decode('utf-8')

        if output.startswith('An error occurred'):
            raise Exception('Error')

        return {'success': True, 'data': output}
    except subprocess.CalledProcessError as e:
        # print("Error", e)
        print_ls.error("Error" + str(e))
        error = {'success': False, 'error': {'title': 'Run Process Check Output Error',
                                             'description': str(' '.join(cmd)) + '\n' + str(e.stderr.decode('utf-8').strip())
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
            await send_message('check call: ' + ' '.join(cmd))
        # sync
        # subprocess.check_call(cmd)

        # Starts the secondary process asynchronously
        process = await asyncio.create_subprocess_exec(*cmd,
                                                       stdout=asyncio.subprocess.PIPE,
                                                       stderr=asyncio.subprocess.STDOUT,)

        # Wait for the completion of the process
        await process.wait()

        return {'success': True}
    except Exception as e:
        error = {'success': False, 'error': {'title': 'Run Process Check Output Error',
                                             'description': str(' '.join(cmd)) + '\n' + str(e)
                                             }
                 }
        return error
