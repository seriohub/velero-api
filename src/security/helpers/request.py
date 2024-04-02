from fastapi import Form


class OAuth2PasswordAndRefreshRequestForm:
    """Modified from fastapi.security.OAuth2PasswordRequestForm"""

    def __init__(
            self,
            grant_type: str = Form(default=None, regex="password|refresh_token"),
            username: str = Form(default=""),
            password: str = Form(default=""),
            refresh_token: str = Form(default=""),
            scope: str = Form(default=""),
            client_id: str | None = Form(default=None),
            client_secret: str | None = Form(default=None),
    ):
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.refresh_token = refresh_token
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret
