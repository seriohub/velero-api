from security.service.authentication import login_service  # , refresh_token_service
from fastapi import Response, Request

async def login_handler(username, password, request: Request, response: Response):
    token = login_service(username, password)

    #
    # uncomment to enable session with cookies (no 1/3)
    #

    # is_secure = request.url.scheme == "https"
    #
    # # Set JWT as HttpOnly cookie
    # response.set_cookie(
    #     key="auth_token",
    #     value=token['access_token'],
    #     httponly=True,
    #     secure=is_secure,
    #     samesite="lax",
    #     max_age=token['expires_in'],
    #     path="/"
    # )

    return token

# async def refresh_login_handler(refresh_token):
#     return refresh_token_service(refresh_token)
