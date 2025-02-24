from security.service.authentication import login_service  # , refresh_token_service


async def login_handler(username, password):
    return login_service(username, password)

# async def refresh_login_handler(refresh_token):
#     return refresh_token_service(refresh_token)
