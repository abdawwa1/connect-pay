from jose import jwt, exceptions
from starlette.authentication import (
    AuthenticationBackend, AuthenticationError, BaseUser, AuthCredentials, UnauthenticatedUser)
from typing import Optional, Tuple, Union
from sql import users_crud
from sql.schemas import UserCreate
from sql.settings import SessionLocal


class JWTUser(BaseUser):
    def __init__(self, id: int, user_name: str, external_id: str) -> None:
        self.id = id
        self.user_name = user_name
        self.external_id = external_id

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.user_name


class KCTokenBackend(AuthenticationBackend):
    execluded_paths = [
        "/docs",
        "/redoc",
        "/openapi.json"
    ]

    def __init__(self,
                 secret_key: str,
                 algorithm: str = 'RS256',
                 prefix: str = 'bearer',
                 username_field: str = 'preferred_username',
                 audience: Optional[str] = None,
                 options: Optional[dict] = None) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.prefix = prefix
        self.username_field = username_field
        self.audience = audience
        self.options = options or dict()

    @classmethod
    def get_token_from_header(cls, authorization: str, prefix: str) -> str:
        """Parses the Authorization header and returns only the token"""
        try:
            scheme, token = authorization.split()
        except ValueError:
            raise AuthenticationError('Could not separate Authorization scheme and token')
        if scheme.lower() != prefix.lower():
            raise AuthenticationError(f'Authorization scheme {scheme} is not supported')
        return token

    def decode_token(self, token: str):
        try:
            payload = jwt.decode(token, key=self.secret_key, algorithms=self.algorithm, audience=self.audience,
                                 options=self.options)
        except exceptions.JWTError as e:
            raise AuthenticationError(str(e))

        return payload

    def sync_user(self, username: str, external_id: str):
        return users_crud.create_user(SessionLocal(), UserCreate(user_name=username, external_id=external_id))

    def get_user(self, external_id: str):
        user = users_crud.get_user(SessionLocal(), external_id=external_id)
        if user:
            return user

    async def authenticate(self, request) -> Union[None, Tuple[AuthCredentials, BaseUser]]:
        if request.url.path in self.execluded_paths:
            return AuthCredentials(), UnauthenticatedUser()

        if "Authorization" not in request.headers:
            raise AuthenticationError("Unauthorized")

        auth = request.headers["Authorization"]
        token = self.get_token_from_header(authorization=auth, prefix=self.prefix)
        payload = self.decode_token(token)
        user = self.get_user(payload.get("sub"))

        if not user:
            user = self.sync_user(payload.get(self.username_field), payload.get("sub"))

        return AuthCredentials(["authenticated"]), JWTUser(id=user.id, user_name=payload[self.username_field],
                                                           external_id=payload.get("sub"))
