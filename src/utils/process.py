import subprocess
import asyncio
import json
from fastapi import WebSocketDisconnect
import os

from configs.config_boot import config_app
from configs.context import current_user_var, cp_user
from ws.websocket_manager import manager

from utils.logger_boot import logger

if config_app.get_enable_nats():
    from integrations.nats_manager import get_nats_manager_instance


async def _send_message(message):
    try:
        logger.debug(message)
        # await manager.broadcast(message)
        user = None
        try:
            user = current_user_var.get()
        except Exception as Ex:
            logger.error(f"send message failed {str(Ex)}")
        finally:
            if config_app.get_enable_nats() and user.is_nats:
                nats_manager = get_nats_manager_instance()
                nc = await nats_manager.get_nats_connection()
                control_plane_user = cp_user.get()
                data = {"user": control_plane_user, "msg": message}
                await nc.publish("socket." + config_app.cluster_id(), json.dumps(data).encode())
                pass
            elif user is not None:
                response = {'type': 'process', 'message': message}
                await manager.send_personal_message(str(user.id), json.dumps(response))

    except WebSocketDisconnect:
        logger.error('send message error')


async def run_check_output_process(cmd, publish_message=True, cwd='./', env=None):
    output = ''
    try:
        if publish_message:
            await _send_message('check output: ' + ' '.join(cmd))

        # Starts the secondary process asynchronously
        process = await asyncio.create_subprocess_exec(*cmd,
                                                       stdout=asyncio.subprocess.PIPE,
                                                       stderr=asyncio.subprocess.STDOUT,
                                                       cwd=cwd,
                                                       env={**os.environ} if not env else env)

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
        logger.error("Error" + str(e))
        error = {'success': False, 'error': {'title': 'Run Process Check Output Error',
                                             'description': str(' '.join(cmd)) + '\n' + str(
                                                 e.stderr.decode('utf-8').strip())
                                             }
                 }
        return error
    except Exception as e:
        # print("Error", e)
        logger.error("Error" + str(e))
        error = {'success': False, 'error': {'title': 'Run Process Check Output Error',
                                             'description': str(e) + ' \n' + str(output)
                                             }
                 }
        return error


# async def run_check_call_process(cmd, publish_message=True):
#     try:
#         if publish_message:
#             await _send_message('check call: ' + ' '.join(cmd))
#
#         # Starts the secondary process asynchronously
#         process = await asyncio.create_subprocess_exec(*cmd,
#                                                        stdout=asyncio.subprocess.PIPE,
#                                                        stderr=asyncio.subprocess.STDOUT, )
#
#         # Wait for the completion of the process
#         await process.wait()
#
#         return {'success': True}
#     except Exception as e:
#         error = {'success': False, 'error': {'title': 'Run Process Check Output Error',
#                                              'description': str(' '.join(cmd)) + '\n' + str(e)
#                                              }
#                  }
#         return error
